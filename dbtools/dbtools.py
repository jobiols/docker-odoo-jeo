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
from datetime import datetime, timedelta
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
import shutil
import logging
import hashlib
import time

colorized = False


# Definir un formato para los logs con colores
class ColorizingStreamHandler(logging.StreamHandler):
    COLORS = {
        "DEBUG": "\033[94m",  # Azul
        "INFO": "\033[92m",  # Verde
        "WARNING": "\033[93m",  # Amarillo
        "ERROR": "\033[91m",  # Rojo
        "CRITICAL": "\033[91m",  # Rojo
        "RESET": "\033[0m",  # Reset de color
    }

    def emit(self, record):
        try:
            msg = self.format(record)
            if colorized:
                color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
                msg = color + msg + self.COLORS["RESET"]
            self.stream.write(msg + "\n")
            self.flush()
        except Exception:
            self.handleError(record)


# Configurar logging para que salga solo en la consola
logging.basicConfig(
    level=logging.INFO,  # Nivel de log
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato del mensaje
    datefmt="%Y-%m-%d %H:%M:%S",  # Formato personalizado para la hora
    handlers=[ColorizingStreamHandler()],  # Usar el handler personalizado
)

params = {}


def get_zip_filename(args):
    """Crear el nombre del archivo hacia el cual hacer backup o restore"""

    if args.backup:
        # BACKUP
        if args.zipfile:
            # Asegurarse de que la ruta base esté incluida si no es absoluta
            if not os.path.isabs(args.zipfile):
                return os.path.join(f"{args.base}/backup_dir", args.zipfile)
            return args.zipfile

        # no tengo el nombre del backup, lo genero con la hora y el cliente
        fecha_hora_local = datetime.now()
        zipfile = fecha_hora_local.strftime(f"{args.db_name}_%Y%m%d_%H_%M_%S")
        return f"{args.base}/backup_dir/{zipfile}.zip"
    else:
        # RESTORE
        if args.zipfile:
            # Asegurarse de que la ruta base esté incluida si no es absoluta
            if not os.path.isabs(args.zipfile):
                return os.path.join(f"{args.base}/backup_dir", args.zipfile)
            return args.zipfile
        else:
            # no tengo el nombre del backup a restaurar, busco el úlimo
            return get_last_backup_file(args)


def get_last_backup_file(args):
    """Obtener el nombre del último backup que se creó"""
    files = glob.glob(f"{args.base}/backup_dir/*.zip")
    if not files:
        logging.info("No backups to restore !")
        exit(1)

    # Filtrar los archivos por el nombre de la base de datos a restaurar
    # Asumiendo que el nombre de la base está al principio del archivo
    backup_key = args.db_name
    filtered_files = [file for file in files if os.path.basename(file).startswith(backup_key)]
    if not filtered_files:
        logging.info(f"No backups found for database '{args.db_name}' to restore!")
        exit(1)

    latest_file = max(filtered_files, key=os.path.getctime)
    logging.info(f"Choosing the latest backup {os.path.basename(latest_file)}")
    return latest_file


def deflate_zip(args, backup_filename, tempdir):
    """Unpack backup and filestore, now expecting binary dump and global roles dump."""

    # Path to the filestore folder
    filestorepath = f"{args.base}/data_dir/filestore"

    try:
        # If the filestore backup folder already exists, delete it
        logging.info(f"Cleaning existing filestore for {args.db_name} if present.")
        shutil.rmtree(f"{filestorepath}/{args.db_name}", ignore_errors=True)
    except Exception as e:
        # Capture unexpected errors during deletion, but don't exit if it's just not found.
        logging.error(
            f"An unexpected error occurred while cleaning filestore: {e}",
            exc_info=True,
        )
        exit(1)

    db_dump_path = None
    globals_dump_path = None

    # Open the ZIP file and extract contents
    with ZipFile(backup_filename, "r") as zip_ref:
        for member in zip_ref.infolist():
            if member.filename.startswith("filestore/"):
                # Extract filestore
                parts = member.filename.split("/", 1)[1]
                member.filename = f"{args.db_name}/{parts}"
                zip_ref.extract(member, filestorepath)
            elif member.filename == "dump.custom":
                # Extract the binary database dump
                zip_ref.extract(member, tempdir)
                db_dump_path = os.path.join(tempdir, "dump.custom")
            elif member.filename == "globals.sql":
                # Extract the global objects dump
                zip_ref.extract(member, tempdir)
                globals_dump_path = os.path.join(tempdir, "globals.sql")
            else:
                logging.warning(f"Unexpected file in zip: {member.filename}. Skipping.")

    if not db_dump_path:
        logging.error("Database dump (dump.custom) not found in the backup file.")
        exit(1)
    if not globals_dump_path:
        logging.warning("Global objects dump (globals.sql) not found in the backup file. Roles might not be restored.")

    # Return the paths to the extracted dump files
    return db_dump_path, globals_dump_path


def killing_db_connections(args, cur):
    logging.info(f"Killing backend connections to {args.db_name}")
    sql = f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{args.db_name}';
        """
    try:
        cur.execute(sql)
        # Give some time for connections to terminate if any
        conn_check_sql = f"SELECT count(*) FROM pg_stat_activity WHERE datname = '{args.db_name}';"
        for _ in range(5): # Retry a few times
            cur.execute(conn_check_sql)
            if cur.fetchone()[0] == 0:
                logging.info(f"All connections to {args.db_name} terminated.")
                break
            logging.debug(f"Still connections active, waiting...")
            time.sleep(1) # Wait a second
        else:
            logging.warning(f"Some connections to {args.db_name} might still be active after retries.")
    except Exception as e:
        logging.error(f"Error terminating connections: {e}", exc_info=True)
        # Do not exit here, continue to drop database if possible.


def drop_database(args, cur):
    logging.info(f"Dropping database '{args.db_name}' if exists")
    sql = f'DROP DATABASE IF EXISTS "{args.db_name}";'
    try:
        cur.execute(sql)
    except Exception as e:
        logging.error(f"Error dropping database: {e}", exc_info=True)
        exit(1)


def create_database(args, cur):
    logging.info(f"Creating database '{args.db_name}'")
    sql = f"""CREATE DATABASE "{args.db_name}"
              OWNER {params.get('db_user', 'odoo')}
              ENCODING 'UTF8'
              TEMPLATE template0;
           """
    try:
        cur.execute(sql)
    except Exception as e:
        logging.error(f"Error creating database: {e}", exc_info=True)
        exit(1)


def do_restore_database(args, backup_filename):
    """Restore database, global objects, and filestore"""

    with tempfile.TemporaryDirectory() as tempdir:

        # Extraer el Filestore al filestore de la estructura y los dumps al temp dir
        logging.info("Deflating zip. Extracting binary dump, global objects, and filestore.")
        db_dump_filename, globals_dump_filename = deflate_zip(args, backup_filename, tempdir)

        # Configurar variable de entorno para la contraseña de la BD
        os.environ["PGPASSWORD"] = params.get("db_password", "odoo")

        # --- 1. Restaurar objetos globales (roles, tablespaces, etc.) ---
        if globals_dump_filename and os.path.exists(globals_dump_filename):
            logging.info("Restoring global objects (roles, tablespaces) from globals.sql")
            try:
                # Conectar a la base de datos 'postgres' para aplicar cambios globales
                process = subprocess.run(
                    [
                        "psql",
                        "-U", f"{params.get('db_user','odoo')}",
                        "-h", f"{params.get('db_host','db')}",
                        "-d", "postgres",  # Conectar a postgres para aplicar roles
                        "-p", f"{params.get('db_port', 5432)}",
                        "-v", "ON_ERROR_STOP=off",
                        "-f", globals_dump_filename,
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                if process.returncode != 0:
                    logging.error(
                        f"Error restoring global objects: {process.stderr}", exc_info=True
                    )
                    # Decide if this is a fatal error. Often, warnings are fine if roles already exist.
                    # For now, let's treat it as a warning unless it's a critical error.
                    logging.warning(f"Global object restoration might have issues (Code {process.returncode}). Continuing with DB restore...")
                else:
                    logging.info("Global objects restored successfully.")
            except FileNotFoundError:
                logging.error(
                    "The 'psql' command was not found. Ensure PostgreSQL client is installed and in the PATH.",
                    exc_info=True,
                )
                exit(1)
            except subprocess.SubprocessError as e:
                logging.error(
                    f"An error occurred while restoring global objects: {e}",
                    exc_info=True,
                )
                exit(1)
            except Exception as e:
                logging.error(f"An unexpected error occurred restoring global objects: {e}", exc_info=True)
                exit(1)
        else:
            logging.warning("No globals.sql found in backup. Skipping global objects restore. Roles might need to be created manually.")

        # --- 2. Restaurar la base de datos principal ---
        logging.info(f"Restoring Database '{args.db_name}' using pg_restore")
        try:
            # Ejecutar el comando pg_restore para restaurar la bd
            process = subprocess.run(
                [
                    "pg_restore",
                    "-U", f"{params.get('db_user','odoo')}",
                    "-h", f"{params.get('db_host','db')}",
                    "-d", f"{args.db_name}",
                    "-p", f"{params.get('db_port', 5432)}",
                    "-j", f"{params.get('db_jobs', 4)}",
                    db_dump_filename,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
            if process.returncode != 0:
                logging.error(
                    f"Error restoring database: {process.stderr}", exc_info=True
                )
                exit(1)
            else:
                logging.info(f"Database '{args.db_name}' restored successfully.")
        except FileNotFoundError:
            logging.error(
                "The 'pg_restore' command was not found. Ensure PostgreSQL client is installed and in the PATH.",
                exc_info=True,
            )
            exit(1)
        except subprocess.SubprocessError as e:
            logging.error(
                f"An error occurred while restoring DB: {e}",
                exc_info=True,
            )
            exit(1)
        except Exception as e:
            logging.error(f"An unexpected error occurred restoring DB: {e}", exc_info=True)
            exit(1)

def sha256sum(filename):
    h = hashlib.sha256()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def backup_database(args):
    """Hacer un backup de la base de datos, en args viene los datos necesarios"""

    # Obtener el lugar donde esta el filestore
    source_filestore = f"{args.base}/data_dir/filestore/{args.db_name}"

    # Obtener el nombre del archivo zip que contendrá el filestore y el dump
    backup_filename = get_zip_filename(args)
    logging.info(
        f"Backing up database {args.db_name} into file {os.path.basename(backup_filename)}"
    )

    # Crear un temp donde armar el backup
    with tempfile.TemporaryDirectory() as tempdir:
        env = os.environ.copy()
        env["PGPASSWORD"] = params["db_password"]

        # --- 1. Crear el dump de objetos globales (roles, tablespaces) ---
        globals_dump_path = os.path.join(tempdir, "globals.sql")
        logging.info(f"Making global objects dump (globals.sql)")
        try:
            cmd_globals = [
                "pg_dumpall",
                "--globals-only",
                f"--host={params['db_host']}",
                f"--port={params['db_port']}",
                f"--username={params['db_user']}",
                f"--file={globals_dump_path}",
            ]
            subprocess.run(cmd_globals, check=True, env=env, stderr=subprocess.PIPE)
            logging.info(f"Global objects dump created.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error during global objects dump: {e.stderr.decode()}", exc_info=True)
            exit(1)
        except Exception as e:
            logging.error(f"An unexpected error occurred during global objects dump: {e}", exc_info=True)
            exit(1)

        # --- 2. Crear el dump de la base de datos (formato custom/binario) ---
        db_dump_path = os.path.join(tempdir, "dump.custom")
        logging.info(f"Making database dump (dump.custom)")
        try:
            cmd_db = [
                "pg_dump",
                f"--dbname={args.db_name}", # Usar args.db_name que es el que se está respaldando
                f"--host={params['db_host']}",
                f"--port={params['db_port']}",
                f"--username={params['db_user']}",
                f"--file={db_dump_path}",
                "--format=custom", # Formato binario personalizado
                # "--no-owner", # Ya no es necesario si pg_dumpall maneja los usuarios
                # "--no-privileges", # Opcional, si no quieres guardar permisos
            ]
            subprocess.run(cmd_db, check=True, env=env, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error during database dump: {e.stderr.decode()}", exc_info=True)
            exit(1)
        except Exception as e:
            logging.error(f"An unexpected error occurred during database dump: {e}", exc_info=True)
            exit(1)

        size = os.path.getsize(db_dump_path) / (1024**3)
        logging.info(f"Database dump file {size:.2f} GB created.")

        # --- 3. Crear el ZIP con ambos dumps y el filestore ---
        try:
            temp_zip_path = os.path.join(tempdir, "backup.zip")
            with ZipFile(temp_zip_path, "w", ZIP_DEFLATED) as zipf:
                # Agregar el dump de la BD
                zipf.write(db_dump_path, "dump.custom")
                logging.info(f"Database dump (dump.custom) added to ZIP.")
                os.remove(db_dump_path)

                # Agregar el dump de objetos globales
                zipf.write(globals_dump_path, "globals.sql")
                logging.info(f"Global objects dump (globals.sql) added to ZIP.")
                os.remove(globals_dump_path) # Borra para optimizar espacio

                logging.info("Adding files from filestore to ZIP.")
                if os.path.exists(source_filestore) and os.path.isdir(source_filestore):
                    for root, dirs, files in os.walk(source_filestore):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # Path relativo dentro del zip
                            arcname = os.path.join("filestore", os.path.relpath(file_path, source_filestore))
                            zipf.write(file_path, arcname)
                            logging.debug(f"Added {arcname}")
                else:
                    logging.warning(f"Filestore directory '{source_filestore}' not found. Skipping filestore backup.")

        except Exception as e:
            logging.error(f"Error creating ZIP file: {e}", exc_info=True)
            exit(1)

        # --- 4. Mover el ZIP al destino final y verificar ---
        try:
            src = temp_zip_path
            dst = backup_filename
            src_hash = sha256sum(src)
            src_size = os.path.getsize(src)

            logging.info(f"copiando archivo de {src} a {dst} usando 'cp'.")

            # Usamos cp como en tu código original para mayor robustez en entornos Docker con volúmenes montados.
            # Esto evita posibles problemas con shutil.copy2 si los sistemas de archivos son diferentes y no soporta hardlinks.
            try:
                subprocess.run(["cp", src, dst], check=True, stderr=subprocess.PIPE)
                logging.info(f"Archivo copiado correctamente de {src} a {dst} usando 'cp'.")
            except subprocess.CalledProcessError as e:
                logging.error(f"Error al ejecutar cp: {e.stderr.decode().strip()}", exc_info=True)
                exit(1)
            except Exception as e:
                logging.error(f"Error inesperado durante la copia con cp: {e}", exc_info=True)
                exit(1)

            # Verificar checksum y tamaño del destino
            dst_hash = sha256sum(dst)
            dst_size = os.path.getsize(dst)

            if src_hash != dst_hash or src_size != dst_size:
                raise ValueError("File copy verification failed: hash or size mismatch")

            logging.info(f"Backup successfully created at {backup_filename}")
        except FileNotFoundError as e:
            logging.error(
                f"File not found: {e}. Ensure the source file exists before moving.",
                exc_info=True,
            )
            exit(1)
        except PermissionError as e:
            logging.error(
                f"Permission denied while moving the backup: {e}. Check directory permissions.",
                exc_info=True,
            )
            exit(1)
        except shutil.Error as e:
            logging.error(f"Error during moving the backup file: {e}", exc_info=True)
            exit(1)
        except Exception as e:
            logging.error(f"An unexpected error occurred moving ZIP: {e}", exc_info=True)
            exit(1)


def cleanup_backup_files(args):
    """Eliminar los backups antiguos que tengan más de args.days_to_keep de
    antiguedad y que empiecen con el nombre de la base"""

    # Solo borra archivos si esta el parametro days_to_keep
    if args.days_to_keep:
        logging.info(f"Cleaning up backups older than {args.days_to_keep} days for {args.db_name}.")
        actual_date = datetime.now()
        max_age = timedelta(days=int(args.days_to_keep))
        backup_dir = f"{args.base}/backup_dir"
        if not os.path.exists(backup_dir):
            logging.warning(f"Backup directory '{backup_dir}' does not exist. Skipping cleanup.")
            return

        deleted_count = 0
        for file in os.listdir(backup_dir):
            # Asume que el nombre de la DB es el prefijo del archivo de backup
            if file.startswith(args.db_name) and file.endswith(".zip"):
                filepath = os.path.join(backup_dir, file)
                if os.path.isfile(filepath):
                    try:
                        file_date = datetime.fromtimestamp(os.path.getmtime(filepath))
                        file_age = actual_date - file_date
                        if file_age > max_age:
                            os.remove(filepath)
                            logging.info(f"Deleted old backup: {file}")
                            deleted_count += 1
                    except Exception as e:
                        logging.warning(f"Could not delete file {file}: {e}")
        if deleted_count == 0:
            logging.info("No old backups found to delete or an error occurred during deletion.")
        else:
            logging.info(f"Successfully deleted {deleted_count} old backup(s).")


def check_parameters(args):
    """Se verifica que esten todos los parametros necesarios si no están se
    buscan en la configuracion del proyecto o en odoo.conf"""

    # ########################### Obtener el manifiesto y el nombre del proyecto
    root_dir = f"{args.base}/sources"
    proyect_name = None
    if os.path.exists(root_dir):
        # Recorrer los directorios en la raíz
        for folder in os.listdir(root_dir):
            folder_path = os.path.join(root_dir, folder)
            # Verificar que es un directorio y el nombre empieza con cl-
            if os.path.isdir(folder_path) and folder.startswith("cl-"):
                # Verificar que es un módulo de Odoo (por ejemplo, buscando __manifest__.py)
                current_proyect_name = folder.removeprefix("cl-")
                manifest_file = os.path.join(folder_path, f"{current_proyect_name}_default", "__manifest__.py")
                if os.path.exists(manifest_file):
                    proyect_name = current_proyect_name
                    params["proyect_name"] = proyect_name
                    # Leer el manifiesto y guardarlo
                    with open(manifest_file, "r", encoding="utf-8") as f:
                        manif = f.read()
                    try:
                        params["manifest"] = ast.literal_eval(manif)
                        break # Found project, exit loop
                    except Exception as e:
                        logging.warning(f"Could not parse manifest for {folder}: {e}")
                        proyect_name = None # Invalidate if manifest is bad
            else:
                logging.debug(f"Skipping non-client folder or non-directory: {folder}")
    else:
        logging.warning(f"Sources directory '{root_dir}' not found. Cannot auto-detect project name.")


    if not proyect_name:
        logging.warning("Could not auto-detect project name from sources. Ensure 'cl-*' folder exists or provide --db-name manually.")
        # If no project name, manifest will be empty, db_name might not be auto-detected correctly.

    # si no viene el nombre de la base de datos construir el default
    if not args.db_name:
        if "manifest" in params and "name" in params["manifest"]:
            args.db_name = f"{params['manifest']['name']}_prod"
            logging.info(f"Auto-detected database name: {args.db_name}")
        else:
            logging.error("Could not determine database name. Please provide it using --db-name.")
            exit(1)

    # Leer datos del archivo odoo.conf
    config_file_path = f"{args.base}/config/odoo.conf"
    config = configparser.ConfigParser()
    if not os.path.exists(config_file_path):
        logging.warning(f"Odoo configuration file '{config_file_path}' not found. Using default DB connection parameters.")
        # Set fallbacks directly if config file is not found
        params["db_name"] = args.db_name # Use the determined db_name
        params["db_host"] = "db"
        params["db_port"] = 5432
        params["db_user"] = "odoo"
        params["db_password"] = "odoo"
    else:
        config.read(config_file_path)
        params["db_name"] = config.get("options", "db_name", fallback=args.db_name)
        params["db_host"] = config.get("options", "db_host", fallback="db")
        params["db_port"] = int(config.get("options", "db_port", fallback=5432)) # Convert to int
        params["db_user"] = config.get("options", "db_user", fallback="odoo")
        params["db_password"] = config.get("options", "db_password", fallback="odoo")

    # Ensure db_name is correctly set in params after all checks
    params["db_name"] = args.db_name


def restore_database(args):

    # Obtener el nombre del backup del cual restaurar
    backup_filename = get_zip_filename(args)
    if not os.path.exists(backup_filename):
        logging.error(f"Backup file not found: {backup_filename}")
        exit(1)

    logging.info(
        f"Restoring {os.path.basename(backup_filename)} into Database {args.db_name}"
    )

    try:
        # Connect to 'postgres' database to ensure we can drop/create the target DB
        conn = psycopg2.connect(
            user=params["db_user"],
            host=params["db_host"],
            port=params["db_port"],
            password=params["db_password"],
            dbname="postgres", # Connect to postgres to perform administrative tasks
            connect_timeout=10 # Add a timeout for connection
        )
    except psycopg2.OperationalError as ex:
        logging.error(f"Failed to connect to PostgreSQL as user '{params['db_user']}' on host '{params['db_host']}:{params['db_port']}'. "
                      f"Please check database credentials, host, port, and ensure the PostgreSQL service is running. Error: {ex}")
        exit(1)
    except Exception as ex:
        logging.error(f"An unexpected error occurred while connecting to the database: {ex}", exc_info=True)
        exit(1)

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    killing_db_connections(args, cur)
    drop_database(args, cur)
    create_database(args, cur)
    # The actual data restoration now happens *after* the database is ready
    do_restore_database(args, backup_filename)

    cur.close()
    conn.close()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Utility for PostgreSQL database backup and restore, including Odoo filestore and global objects."
    )
    arg_parser.add_argument(
        "--base",
        default="/base",
        help="Project base directory (e.g., /odoo_ar/odoo-16.0e/bukito). Default: /base",
    )
    arg_parser.add_argument(
        "--db-name",
        help="Database name to restore into or backup from. If omitted, it will try to auto-detect from project manifest "
        "(__manifest__.py) or use a default.",
    )
    arg_parser.add_argument(
        "--zipfile",
        help="The specific backup filename (e.g., /path/to/my_backup.zip). "
        "On restore, if omitted, defaults to the last backup file in BASE/backup_dir. "
        "On backup, if omitted, defaults to a timestamped filename in BASE/backup_dir.",
    )
    arg_parser.add_argument(
        "--days-to-keep",
        type=int, # Ensure it's an integer
        help="Number of days to keep backups. If omitted, no old backups will be deleted during a backup operation.",
    )
    arg_parser.add_argument(
        "--restore",
        action="store_true",
        help="Restore database. This parameter is mutually exclusive with --backup.",
    )
    arg_parser.add_argument(
        "--db-jobs",
        type=int,
        default=4,
        help="Number of jobs to use for parallel restore. Default: 4. "
        "This is only used when restoring a database.",
    )
    arg_parser.add_argument(
        "--backup",
        action="store_true",
        help="Backup database. This parameter is mutually exclusive with --restore.",
    )
    args = arg_parser.parse_args()

    # Basic argument validation
    if not (args.restore or args.backup):
        logging.error("You must specify either --backup or --restore.")
        arg_parser.print_help()
        exit(1)
    if args.restore and args.backup:
        logging.error("You must issue a backup or a restore command, not both.")
        exit(1)

    logging.info("Database utils V1.5.0 (Binary Format & Global Objects)")

    # Check and load parameters (this must happen before any DB operation)
    check_parameters(args)

    if args.restore:
        restore_database(args)
        logging.info(f"Database {args.db_name} successfully restored from {os.path.basename(get_zip_filename(args))}")

    if args.backup:
        backup_database(args)
        cleanup_backup_files(args)
        logging.info(f"Database {args.db_name} successfully backed up to {os.path.basename(get_zip_filename(args))}")