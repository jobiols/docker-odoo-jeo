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
import os, glob
import datetime
from zipfile import ZipFile
import zipfile
import shutil
import logging

# Configurar logging para que salga solo en la consola
logging.basicConfig(
    level=logging.DEBUG,  # Nivel de log
    format='%(asctime)s - %(levelname)s - %(message)s',  # Formato del mensaje
    datefmt='%H:%M:%S'  # Formato personalizado para la hora
)

params = {}
rojo = "\033[91m"
resetear_color = "\033[0m"

# def log_time():
#     time = datetime.datetime.now()
#     return time.strftime('%H:%m:%S')

def get_zip_filename(args):
    """Crear el nombre del archivo hacia el cual backupear o restaurar"""

    if args.backup:
        # BACKUP
        if not args.zipfile:
            # no tengo el nombre del backup, lo genero con la hora y el cliente
            fecha_hora_local = datetime.datetime.now()
            zipfile = fecha_hora_local.strftime(f"{args.db_name}_%Y%m%d_%H_%M_%S")
            return f"{args.base}/backup_dir/{zipfile}"
    else:
        # RESTORE
        if not args.zipfile:
            # no tengo el nombre del restore, busco el úlimo
            return get_last_backup_file(args)

    # si me viene el parametro args.zipfile ese es el nombre que voy a usar sin
    # importar si es backup o restore
    return f"{args.base}/backup_dir/{args.zipfile}"


def get_last_backup_file(args):
    """Obtener el nombre del último backup que se creó"""

    files = glob.glob(f"{args.base}/backup_dir/{args.db_name}*.zip")
    for file in files:
        logging.info(f"Existing Backup {file}")
    if files:
        backup_filename = max(files, key=os.path.getctime)
        logging.info(f"Choosing the latest backup {os.path.basename(backup_filename)}")
        return backup_filename
    else:
        logging.info("No backups to restore !")
        exit(1)


def deflate_zip(args, backup_filename, tempdir):
    """Unpack backup and filestore"""

    # Path to the filestore folder
    filestorepath = f"{args.base}/data_dir/filestore"

    # If the filestore backup folder already exists, delete it
    shutil.rmtree(f"{filestorepath}/{args.db_name}", ignore_errors=True)

    # Open the ZIP file
    with ZipFile(backup_filename, "r") as zip_ref:

        # Extraer todo el dump al temporario y el filestore a su lugar
        with zipfile.ZipFile(backup_filename, "r") as zip_ref:
            for member in zip_ref.infolist():
                if member.filename.startswith('filestore'):
                    parts = member.filename.split('/',1)[1]
                    member.filename = f"{args.db_name}/{parts}"
                    zip_ref.extract(member,filestorepath)
                    extractpath = os.path.join(filestorepath, member.filename)
                else:
                    zip_ref.extract(member, tempdir)
                    extractpath = os.path.join(tempdir, member.filename)

                permissions = member.external_attr >> 16
                os.chmod(extractpath, permissions)

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
    sql = f"DROP DATABASE IF EXISTS {args.db_name};"
    cur.execute(sql)

def create_database(args, cur):
    logging.info("Creating database")
    sql = f"CREATE DATABASE {args.db_name};"
    cur.execute(sql)

def do_restore_database(args, backup_filename):
    """Restore database and filestore"""

    with tempfile.TemporaryDirectory() as tempdir:

        # Extraer el Filestore al filestore de la estructura y el backup al temp dir
        logging.info( "Deflating zip")
        dump_filename = deflate_zip(args, backup_filename, tempdir)
        with open(dump_filename, "r") as d_filename:
            # Run psql command as a subprocess, and specify that the dump file should
            # be passed as standard input to the psql process
            os.environ["PGPASSWORD"] = params.get("db_password", "odoo")
            logging.info("Restoring Database")
            process = subprocess.run(
                [
                    "psql", "-U", f"{params.get('db_user','odoo')}",
                    "-h", f"{params.get('db_host','db')}",
                    "-d", f"{args.db_name}",
                    "-p", f"{params.get('db_port', 5432)}",
                ],
                stdout=subprocess.PIPE,
                stdin=d_filename,
            )

def backup_database(args):
    """Hacer un backup de la base de datos"""

    # Obtener el nombre del restore
    backup_filename = get_zip_filename(args)
    logging.info(f"Backing up database {args.db_name} into file {backup_filename}")

    # Crear un temp donde armar el backup
    with tempfile.TemporaryDirectory() as tempdir:
        os.environ["PGPASSWORD"] = params["db_password"]
        # Crear el dump
        try:
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
            logging.info(f"Error en backup {e}")
            exit(1)

        # Crear el zip y agregarle el filestore
        # copiar el filestore a tempdir
        shutil.copytree(
            f"{args.base}/data_dir/filestore/{args.db_name}",
            f"{tempdir}/filestore",
        )

        # zipear y mover al archivo destino
        shutil.make_archive(backup_filename, "zip", tempdir)


def cleanup_backup_files(args):
    """Elimiar los backups antiguos que tengan más de args.days_to_keep de antiguedad"""

    # sin el parametro termina
    if not args.days_to_keep:
        return

    actual_date = datetime.datetime.now()
    max_age = datetime.timedelta(days=int(args.days_to_keep))
    backup_dir = f"{args.base}/backup_dir"
    for file in os.listdir(backup_dir):
        filepath = os.path.join(backup_dir, file)
        if os.path.isfile(filepath):
            file_date = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
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
        print('proyect {proyect_name}_default not found!')
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

    # Obtener el nombre del backup
    backup_filename = get_zip_filename(args)
    logging.info(f"Restoring {backup_filename} into Database {args.db_name}")

    try:
        # Crear conexion a la base de datos
        conn = psycopg2.connect(
            user=params["db_user"],
            host=params["db_host"],
            port=params["db_port"],
            password=params["db_password"],
            dbname="postgres",
        )
    except Exception as ex:
        logging.info(
            "No se puede conectar a la BD esta el servidor postgres corriendo?", str(ex)
        )
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

    logging.info(f"Database utils V1.4.4")
    print()

    check_parameters(args)

    if args.restore:
        restore_database(args)
        logging.info(
            f"{rojo}RESTORE TO {args.db_name} DATABASE IS FIHISHED , "
            f"WARNING - DATABASE IS EXACT {resetear_color}"
        )

    if args.backup:
        backup_database(args)
        cleanup_backup_files(args)
        logging.info("database backed up")
