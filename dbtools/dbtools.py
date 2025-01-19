#!/usr/bin/env python3
#
# Script que se ejecuta al lanzar la imagen
#

import os
import ast
import configparser
import argparse
import subprocess
import tempfile
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import glob
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
import shutil
import logging

# Definir un formato para los logs con colores
class ColorizingStreamHandler(logging.StreamHandler):
    COLORS = {
        'DEBUG': '\033[94m',  # Azul
        'INFO': '\033[92m',   # Verde
        'WARNING': '\033[93m',  # Amarillo
        'ERROR': '\033[91m',   # Rojo
        'CRITICAL': '\033[91m', # Rojo
        'RESET': '\033[0m'      # Reset de color
    }
    def emit(self, record):
        try:
            msg = self.format(record)
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            self.stream.write(color + msg + self.COLORS['RESET'] + '\n')
            self.flush()
        except Exception:
            self.handleError(record)

# Configurar logging para que salga solo en la consola
logging.basicConfig(
    level=logging.INFO,  # Nivel de log
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato del mensaje
    datefmt="%H:%M:%S",  # Formato personalizado para la hora
    handlers=[ColorizingStreamHandler()]  # Usar el handler personalizado
)

params = {}

def get_zip_filename(args):
    """Crear el nombre del archivo hacia el cual hacer backup o restore"""

    if args.backup:
        # BACKUP
        if args.zipfile:
            return args.zipfile

        # no tengo el nombre del backup, lo genero con la hora y el cliente
        fecha_hora_local = datetime.now()
        zipfile = fecha_hora_local.strftime(f"{args.db_name}_%Y%m%d_%H_%M_%S")
        return f"{args.base}/backup_dir/{zipfile}.zip"
    else:
        # RESTORE
        if args.zipfile:
            return args.zipfile
        else:
            # no tengo el nombre del backup a restaurar, busco el úlimo
            return get_last_backup_file(args)

    # si me viene el parametro args.zipfile ese es el nombre que voy a usar sin
    # importar si es backup o restore
    return f"{args.base}/backup_dir/{args.zipfile}"


def get_last_backup_file(args):
    """Obtener el nombre del último backup que se creó"""
    files = glob.glob(f"{args.base}/backup_dir/*.zip")
    if not files:
        logging.info("No backups to restore !")
        exit(1)

    # Filtrar los archivos por el nombre de la BD a restaurar
    filtered_files = [file for file in files if args.db_name in file]
    if not filtered_files:
        logging.info("No backups to restore !")
        exit(1)

    latest_file = max(filtered_files, key=os.path.getctime)
    logging.info(f"Choosing the latest backup {os.path.basename(latest_file)}")
    return latest_file


def deflate_zip(args, backup_filename, tempdir):
    """Unpack backup and filestore"""

    # Path to the filestore folder
    filestorepath = f"{args.base}/data_dir/filestore"

    # If the filestore backup folder already exists, delete it
    #    shutil.rmtree(f"{filestorepath}/{args.db_name}")
    try:
        # If the filestore backup folder already exists, delete it
        shutil.rmtree(f"{filestorepath}/{args.db_name}")
    except FileNotFoundError:
        logging.warning(
            f"The directory {filestorepath}/{args.db_name} does not exist. Skipping deletion."
        )
    except PermissionError as e:
        logging.error(
            f"Permission denied while attempting to delete {filestorepath}/{args.db_name}: {e}"
        )
        exit(1)
    except shutil.Error as e:
        logging.error(
            f"Error occurred while deleting the directory {filestorepath}/{args.db_name}: {e}"
        )
        exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred while deleting the directory: {e}")
        exit(1)

    # Open the ZIP file
    with ZipFile(backup_filename, "r") as zip_ref:

        # Extraer todo el dump al temporario y el filestore a su lugar
        with ZipFile(backup_filename, "r") as zip_ref:
            for member in zip_ref.infolist():
                if member.filename.startswith("filestore"):
                    parts = member.filename.split("/", 1)[1]
                    member.filename = f"{args.db_name}/{parts}"
                    zip_ref.extract(member, filestorepath)
                else:
                    zip_ref.extract(member, tempdir)

    # Return the full path to the database dump file in the temporary directory
    return f"{tempdir}/dump.sql"


def killing_db_connections(args, cur):
    logging.info(f"Killing backend connections to {args.db_name}")
    sql = f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{args.db_name}';
        """
    cur.execute(sql)


def drop_database(args, cur):
    logging.info("Dropping database if exists")
    sql = f'DROP DATABASE IF EXISTS "{args.db_name}";'
    cur.execute(sql)


def create_database(args, cur):
    logging.info("Creating database")
    sql = f'CREATE DATABASE "{args.db_name}";'
    cur.execute(sql)


def do_restore_database(args, backup_filename):
    """Restore database and filestore"""

    with tempfile.TemporaryDirectory() as tempdir:

        # Extraer el Filestore al filestore de la estructura y el backup al temp dir
        logging.info("Deflating zip")
        dump_filename = deflate_zip(args, backup_filename, tempdir)
        with open(dump_filename, "r") as d_filename:
            # Configurar varialble de entorno para la contraseña de la BD
            os.environ["PGPASSWORD"] = params.get("db_password", "odoo")
            logging.info("Restoring Database")
            try:
                # Ejecutar el compando psql para restaurar la bc
                process = subprocess.run(
                    [
                        "psql",
                        "-U",
                        f"{params.get('db_user','odoo')}",
                        "-h",
                        f"{params.get('db_host','db')}",
                        "-d",
                        f"{args.db_name}",
                        "-p",
                        f"{params.get('db_port', 5432)}",
                    ],
                    stdout=subprocess.DEVNULL,  # No capturar stdout
                    stderr=subprocess.PIPE,
                    stdin=d_filename,
                    text=True,
                )
                if process.returncode != 0:
                    logging.error(f"Error restoring database: {process.stderr}")
                    exit(1)
            except FileNotFoundError:
                logging.error(
                    "The 'psql' command was not found. Ensure PostgreSQL is installed and in the PATH."
                )
                exit(1)
            except subprocess.SubprocessError as e:
                logging.error(
                    f"An error occurred while running the 'psql' command: {e}"
                )
                exit(1)


def backup_database(args):
    """Hacer un backup de la base de datos, en args viene los datos necesarios"""

    # Obtener el lugar donde esta el filestore
    source = f"{args.base}/data_dir/filestore/{args.db_name}"

    # Obtener el nombre del archivo zip que contendrá el filestore y el dump
    backup_filename = get_zip_filename(args)
    logging.info(f"Backing up database {args.db_name} into file {os.path.basename(backup_filename)}")

    # Crear un temp donde armar el backup
    with tempfile.TemporaryDirectory() as tempdir:
        os.environ["PGPASSWORD"] = params["db_password"]
        # Crear el dump
        try:
            logging.info(f"Making dump file")
            cmd = [
                "pg_dump",
                f"--dbname={params['db_name']}",
                f"--host={params['db_host']}",
                f"--username={params['db_user']}",
                f"--file={tempdir}/dump.sql",
                "--no-owner",
            ]
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error en backup {e}")
            exit(1)

        size = os.path.getsize(f"{tempdir}/dump.sql") / (1024 ** 3)
        logging.info(f"Dump file {size:.2f} GB created")

        # Crear el ZIP
        try:
            with ZipFile(f"{tempdir}/backup.zip", "w", ZIP_DEFLATED) as zipf:
                # Generar el dump de la BD y agregarlo directamente al ZIP
                zipf.write(f"{tempdir}/dump.sql", "dump.sql")
                logging.info(f"Database dump added to ZIP")
                os.remove(f"{tempdir}/dump.sql")  # Borra para optimizar espacio

                logging.info("Adding files from filestore to ZIP")
                for root, dirs, files in os.walk(source):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Path relativo dentro del zip
                        arcname = file_path.replace(source, "/filestore")
                        zipf.write(file_path, arcname)
                        logging.debug(f"Added {arcname}")
        except Exception as e:
            logging.error(f"Error creando archivo ZIP: {e}")
            exit(1)

        try:
            # Copiar el backup al directorio final
            shutil.move(f"{tempdir}/backup.zip", backup_filename)
            logging.info(f"Backup successfully created {backup_filename}")
        except FileNotFoundError as e:
            logging.error(
                f"File not found: {e}. Ensure the source file exists before moving."
            )
            exit(1)
        except PermissionError as e:
            logging.error(
                f"Permission denied while moving the backup: {e}. Check directory permissions."
            )
            exit(1)
        except shutil.Error as e:
            logging.error(f"Error during moving the backup file: {e}")
            exit(1)
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            exit(1)


def cleanup_backup_files(args):
    """Elimiar los backups antiguos que tengan más de args.days_to_keep de
    antiguedad y que empiecen con el nombre de la base"""

    # Solo borra archivos si esta el parametro days_to_keep
    if args.days_to_keep:
        actual_date = datetime.now()
        max_age = datetime.timedelta(days=int(args.days_to_keep))
        backup_dir = f"{args.base}/backup_dir"
        for file in os.listdir(backup_dir):
            if file.startswith(args.db_name):
                filepath = os.path.join(backup_dir, file)
                if os.path.isfile(filepath):
                    file_date = datetime.fromtimestamp(os.path.getmtime(filepath))
                    file_age = actual_date - file_date
                    if file_age > max_age:
                        os.remove(filepath)


def check_parameters(args):
    """Se verifica que esten todos los parametros necesarios si no están se
    buscan en la configuracion del proyecto o en odoo.conf"""

    # ########################### Obtener el manifiesto y el nombre del proyecto
    root_dir = f"{args.base}/sources"
    # Recorrer los directorios en la raíz
    for folder in os.listdir(root_dir):
        folder_path = os.path.join(root_dir, folder)
        # Verificar que es un directorio y el nombre empieza con cl-
        if os.path.isdir(folder_path) and folder.startswith("cl-"):
            # Verificar que es un módulo
            proyect_name = folder.removeprefix("cl-")
            manifest_file = f"{folder}/{proyect_name}_default/__manifest__.py"
            if os.path.exists(f"{root_dir}/{manifest_file}"):
                params["proyect_name"] = proyect_name
                # Leer el manifiesto y guardarlo
                with open(f"{root_dir}/{manifest_file}", "r", encoding="utf-8") as f:
                    manif = f.read()
                params["manifest"] = ast.literal_eval(manif)
                break

    if not params:
        print("proyect {proyect_name}_default not found!")
        exit(1)

    # si no viene el nombre de la base de datos construir el default
    if not args.db_name:
        args.db_name = f"{params['manifest']['name']}_prod"

    # Leer datos del archivo odoo.conf
    config = configparser.ConfigParser()
    config.read(f"{args.base}/config/odoo.conf")

    params["db_name"] = config.get("options", "db_name", fallback=args.db_name)
    params["db_host"] = config.get("options", "db_host", fallback="db")
    params["db_port"] = config.get("options", "db_port", fallback=5432)
    params["db_user"] = config.get("options", "db_user", fallback="odoo")
    params["db_password"] = config.get("options", "db_password", fallback="odoo")


def restore_database(args):

    # Obtener el nombre del backup del cual restaurar
    backup_filename = get_zip_filename(args)
    logging.info(f"Restoring {os.path.basename(backup_filename)} into Database {args.db_name}")

    try:
        conn = psycopg2.connect(
            user=params["db_user"],
            host=params["db_host"],
            port=params["db_port"],
            password=params["db_password"],
            dbname="postgres",
        )
    except Exception as ex:
        logging.info(f"No se puede conectar a la BD, Error {ex}")
        exit()

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    killing_db_connections(args, cur)
    drop_database(args, cur)
    create_database(args, cur)
    do_restore_database(args, backup_filename)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--base",
        default="/base",
        help="Proyect dir, (i.e. /odoo_ar/odoo-16.0e/bukito)",
    )
    arg_parser.add_argument(
        "--db-name",
        help="Database name to restore into or tu backup from, if ommited "
        "default database is used.",
    )
    arg_parser.add_argument(
        "--zipfile",
        help="The backup filename.\n"
        "On restore, defaults to the last backup file in BASE/backup_dir. "
        "On backup, defaults to a filename with a timestamp",
    )
    arg_parser.add_argument(
        "--days-to-keep",
        help="Number of days to keep backups, if ommited, none of the old "
        "backups wil be deleted",
    )
    arg_parser.add_argument(
        "--restore",
        action="store_true",
        help="Restore database. This parameter is mutually exclusive with --backup",
    )
    arg_parser.add_argument(
        "--backup",
        action="store_true",
        help="Backup database. This parameter is mutually exclusive with --restore",
    )
    arg_parser.add_argument(
        "--no-neutralize",
        action="store_true",
        help="Make an exact database (no neutralize) if omitted, a neutralized "
        "restore will be generated; this does not work with --backup.",
    )
    args = arg_parser.parse_args()
    if args.restore and args.backup:
        logging.info("You must issue a backup or a restore command, not both")
        exit()

    logging.info(f"Database utils V1.4.6")

    check_parameters(args)

    if args.restore:
        restore_database(args)
        logging.info(f"Database {args.db_name} successfully restored")

    if args.backup:
        backup_database(args)
        cleanup_backup_files(args)
        logging.info(f"Database backed {args.db_name} successfully backed up")
