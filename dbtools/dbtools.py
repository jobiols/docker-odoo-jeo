#!/usr/bin/env python3
#
# Script que se ejecuta al lanzar la imagen
#
import io
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
import pytz


params = {}

def get_zip_filename(args):
    """Obtener el nombre del archivo hacia el cual backupear
    El nombre del archivo para salvar el backup se obtiene del parametro
    args.zipfile.
    Si el archivo ya existe se termina con error.
    Si no se especificó el nombre del archivo, se crea un nombre con la fecha
    y la hora en GMT-3
    """
    if args.zipfile:
        backup_filename = f"{args.base}/backup_dir/{args.zipfile}"
        # Verificaciones
        if args.backup:
            if os.path.exists(backup_filename):
                print(f"The file {args.zipfile} already exists")
                exit()
        else:
            if not os.path.exists(backup_filename):
                print(f"The file {args.zipfile} does not exists")
                exit()
    else:
        fecha_hora_local = datetime.datetime.now()
        zipfile = fecha_hora_local.strftime("bkp_%Y%m%d_%H:%M:%S")

    print(f"The backup file is {zipfile}")
    return f"{args.base}/backup_dir/{zipfile}"


def deflate_zip(args, backup_filename, tempdir):
    """Unpack backup and filestore"""

    # Path to the filestore folder
    filestorepath = f"{args.base}/data_dir/filestore/{args.db_name}"

    # If the filestore folder already exists, delete it
    if os.path.exists(filestorepath):
        shutil.rmtree(filestorepath)

    # Open the ZIP file
    with ZipFile(backup_filename, "r") as zip_ref:

        # Extraer todo el zip al temporario
        with ZipFile(backup_filename, "r") as zip_ref:
            zip_ref.extractall(path=tempdir)

        # copiar el filestore al destino
        shutil.copytree(f"{tempdir}/filestore", filestorepath)

    # fix the filestore owner o sea si lo crea le pone root y fallará
    # No encuentro manera de ponerle lo mismo que cuando odoo lo crea
    # uinfo = pwd.getpwnam("systemd-resolve")
    # ginfo = grp.getgrnam("systemd-journal")
    # uid = uinfo.pw_uid
    # gid = ginfo.gr_gid
    # os.chown(f"{args.base}/data_dir/filestore", uid, gid)

    # Return the full path to the database dump file in the temporary directory
    return f"{tempdir}/dump.sql"


def killing_db_connections(args, cur):
    print(f"Killing backend connections to {args.db_name}")
    sql = f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{args.db_name}';
        """
    cur.execute(sql)


def drop_database(args, cur):
    print("Dropping database if exists")
    sql = f"DROP DATABASE IF EXISTS {args.db_name};"
    cur.execute(sql)


def create_database(args, cur):
    print("Creating database")
    sql = f"CREATE DATABASE {args.db_name};"
    cur.execute(sql)


def do_restore_database(args, backup_filename, credentials):
    """Restore database and filestore"""

    with tempfile.TemporaryDirectory() as tempdir:
        # Extraer el Filestore al filestore de la estructura y el backup al temp dir
        dump_filename = deflate_zip(args, backup_filename, tempdir)
        with open(dump_filename, "r") as d_filename:
            # Run psql command as a subprocess, and specify that the dump file should
            # be passed as standard input to the psql process
            os.environ["PGPASSWORD"] = credentials.get("db_password", "odoo")
            print("Restoring Database")
            process = subprocess.run(
                [
                    "psql",
                    "-U",
                    f"{credentials.get('db_user','odoo')}",
                    "-h",
                    f"{credentials.get('db_host','db')}",
                    "-d",
                    f"{args.db_name}",
                ],
                stdout=subprocess.PIPE,
                stdin=d_filename,
            )


def neutralize_database(args, cur):
    """Neutralizar base de datos luego de hacer el restore"""

    # Obtener la imagen desde el cl
    sources = f"{args.base}/sources"
    for root, dirs, files in os.walk(sources):
        if "__manifest__.py" in files:
            # Esto se trae todos los manifest que pueden ser montones
            manifest = f"{root}/__manifest__.py"
            with open(manifest, "r") as f:
                man = f.read()
            # Verifica si tiene la key docker-images y termina
            data = ast.literal_eval(man)
            if data.get("docker-images"):
                break

    for image in data.get("docker-images"):
        if "odoo" in image:
            break
    image = image.split()[1]

    # Lanzar la imagen y ejecutar neutralize
    cmd = (
        "sudo docker run --rm -it --network host "
        f"-v {args.base}/config:/opt/odoo/etc/ "
        f"-v {args.base}/data_dir:/opt/odoo/data "
        f"-v {args.base}/sources:/opt/odoo/custom-addons "
        f"{image} odoo neutralize -d {args.db_name} "
    )

    try:
        result = subprocess.run(
            cmd, shell=True, check=True, text=True, capture_output=True
        )
        print(result.stdout)  # Imprime la salida estándar del comando
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e}")
        print(e.stdout)  # Mostrar la salida estándar en caso de error
        print(e.stderr)  # Mostrar la salida de error estándar


def get_backup_filename(args):
    """Obtener nombre del backup a restaurar
    El nombre del backup a restaurar viene en args.zipfile
    si el argumento viene vacío entonces se obtiene el nombre del último backup
    que se hizo.
    Finalmente si no hay ningún backup termina con error
    """

    if args.zipfile:
        backup_filename = f"{args.base}/backup_dir/{args.zipfile}"
        print("The selected backup is " + backup_filename)
        return backup_filename
    else:
        files = glob.glob("%s/backup_dir/*.zip" % args.base)
        if files:
            backup_filename = max(files, key=os.path.getctime)
            print(f"Choosing the latest backup {os.path.basename(backup_filename)}")
            return backup_filename
        else:
            print("No backups to restore !")
            exit()

def backup_database(args):
    """ Hacer un backup de la base de datos"""

    # Obtener el nombre del restore
    backup_filename = get_zip_filename(args)
    print(f"Backing up database {args.db_name} into file {backup_filename}")

    # Crear un temp donde armar el backup
    with tempfile.TemporaryDirectory() as tempdir:

        # copiar el filestore a tempdir
        shutil.copytree(
            f"{args.base}/data_dir/filestore/{args.db_name}", f"{tempdir}/filestore/{args.db_name}"
        )
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
            print(f"error en backup {e}")
            exit()

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
        if os.path.isdir(folder_path) and folder.startswith('cl-'):
            # Verificar que es un módulo 
            proyect_name = folder.lstrip('cl-')
            manifest_file = f"{folder}/{proyect_name}_default/__manifest__.py"
            if os.path.exists(f"{root_dir}/{manifest_file}"):
                params['proyect_name'] = proyect_name
                # Leer el manifiesto y guardarlo
                with open(f"{root_dir}/{manifest_file}" , 'r',encoding='utf-8') as f:
                    manif = f.read()
                params['manifest'] = ast.literal_eval(manif)
                break

    # si no viene el nombre de la base de datos construir el default
    if not args.db_name:
        args.db_name = f"{params['manifest']['name']}_prod"

    # Leer datos del archivo odoo.conf
    config = configparser.ConfigParser()
    config.read(f"{args.base}/config/odoo.conf")

    params['db_name'] = config.get("options", "db_name", fallback=args.db_name)
    params['db_host'] = config.get("options", "db_host", fallback="db")
    params['db_port'] = config.get("options", "db_port", fallback=5432)
    params['db_user'] = config.get("options", "db_user", fallback="odoo")
    params['db_password'] = config.get("options", "db_password", fallback="odoo")


def restore_database(args):
    if not args.db_name:
        print("Missing --db-name argument")

    # Obtener el nombre del backup
    backup_filename = get_zip_filename(args)
    print(f"Restoring {backup_filename} into Database {args.db_name}")

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    killing_db_connections(args, cur)
    drop_database(args, cur)
    create_database(args, cur)
    do_restore_database(args, backup_filename, credentials)

    rojo = "\033[91m"
    resetear_color = "\033[0m"

    if args.no_neutralize:
        print(
            f"{rojo}RESTORE TO {args.db_name} DATABASE IS FIHISHED , "
            f"WARNING - DATABASE IS NOT NEUTRALIZED - WARNING {resetear_color}"
        )
    else:
        neutralize_database(args, credentials)
        print(f"RESTORE FIHISHED FOR {args.db_name}, " "DATABASE IS NEUTRALIZED")


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
        print("Yu must issue a backup or a restore command, not both")
        exit()

    print("Database utils V1.4.1")
    print()

    check_parameters(args)

    if args.restore:
        restore_database(args)
    if args.backup:
        backup_database(args)
        cleanup_backup_files(args)
        print("database backed up")
