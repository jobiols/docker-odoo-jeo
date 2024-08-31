#!/usr/bin/env python3
#
# Script que se ejecuta al lanzar la imagen
#
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


def get_restore_filename(args):
    """ Obtener el nombre del archivo hacia el cual backupear
        El nombre del archivo para salvar el backup se obtiene del parametro
        args.zipfile.
        Si el archivo ya existe se termina con error.
        Si no se especificó el nombre del archivo, se crea un nombre con la fecha
        y la hora en GMT-3
    """
    if args.zipfile:
        backup_filename = f"{args.base}/backup_dir/{args.zipfile}"
        # Verificar si el archivo existe y terminar con error
        if os.path.exists(backup_filename):
            print(f"The file {args.zipfile} already exists")
            exit()
    else:
        fecha_hora_local = datetime.datetime.now(
            pytz.timezone("America/Argentina/Buenos_Aires")
        )
        zipfile = fecha_hora_local.strftime("bkp_%Y-%m-%d_%H-%M-%S_GMT-3")

    print(f"The new backup file is {zipfile}")
    return f"{args.base}/backup_dir/{zipfile}"


def get_backup_filename(args):
    """ Obtener nombre del backup a restaurar
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
        shutil.copytree(tempdir+'/filestore', filestorepath)

        # remover lo que sobra del destino
        shutil.rmtree(filestorepath + 'filestore')
        os.remove(filestorepath + 'dump.sql')

    # fix the filestore owner o sea si lo crea le pone root y fallará
    # No encuentro manera de ponerle lo mismo que cuando odoo lo crea
    # uinfo = pwd.getpwnam("systemd-resolve")
    # ginfo = grp.getgrnam("systemd-journal")
    # uid = uinfo.pw_uid
    # gid = ginfo.gr_gid
    # os.chown(f"{args.base}/data_dir/filestore", uid, gid)

    # Return the full path to the database dump file in the temporary directory
    return tempdir + "/dump.sql"


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


def do_restore_database(args, backup_filename):
    """Restore database and filestore"""
    import requests
    import io
    from werkzeug.datastructures import FileStorage

    # <class 'werkzeug.datastructures.FileStorage'>
    odoo_container = 'lopez'
    print('do_restore_database ---------------------------------', backup_filename)

    with open(backup_filename, 'rb') as file:
        backup = file.read()
    backup_file = FileStorage(stream=io.BytesIO(backup), filename=backup_filename, content_type='application/zip')

    print('se leyo el archivo de backup')

    url = f"http://{odoo_container}:8069/web/database/restore"
    master_pwd = 'lopez-23'
    db_name = 'lopez_test_0102'
    neutralize_database = 'on'

    data = {
        'master_pwd': master_pwd,
        'backup_file': backup_file,
        'name': db_name,
        'copy': 'false',
        'neutralize_database': neutralize_database,
    }
    import json
    try:
        answer = requests.post(url, data=json.dumps(data))
    except Exception as ex:
        print('No se puede enviar post odoo ',str(ex))
        exit()
    if answer.status_code != 200:
        print('>>>>>>>>>>',answer,answer.text)
        exit()

    print('respuesta sin error -------------------',answer)
    exit()
    # with tempfile.TemporaryDirectory() as tempdir:
    #     # Extraer el Filestore al filestore de la estructura y el backup al temp dir
    #     dump_filename = deflate_zip(args, backup_filename, tempdir)
    #     with open(dump_filename, "r") as d_filename:
    #         # Run psql command as a subprocess, and specify that the dump file should
    #         # be passed as standard input to the psql process
    #         os.environ["PGPASSWORD"] = "odoo"
    #         print("Restoring Database")
    #         process = subprocess.run(
    #             ["psql", "-U", "odoo", "-h", "db", "-d", "%s" % args.db_name],
    #             stdout=subprocess.PIPE,
    #             stdin=d_filename,
    #         )

    #     if int(process.returncode) != 0:
    #         print(f"The restored proces end with error {process.returncode}")
    #         exit(1)


def neutralize_database(args, cur):
    """Neutralizar base de datos luego de hacer el restore"""

    #obtener todos los archivos neutralize.sql
    # sudo docker exec -it odoo find -name neutralize.sql

    sql = """

    """

    cur.execute(sql)


def get_credentials(config_path):
    """Leer el archivo de configuración y extrar credenciales postgres
        db_name, db_host, db_port, db_user, db_password
    """
    config = configparser.ConfigParser()
    config.read(config_path)

    db_name = config.get('options', 'db_name', fallback=args.db_name)
    db_host = config.get('options', 'db_host', fallback='db')
    db_port = config.get('options', 'db_port', fallback=5432)
    db_user = config.get('options', 'db_user', fallback='odoo')
    db_password = config.get('options', 'db_password', fallback='odoo')
    return {
        'db_name': db_name,
        'db_host': db_host,
        'db_port': db_port,
        'db_user': db_user,
        'db_password': db_password
    }

def backup_database(args):
    """Para hacer un backup necesitamos saber si lo vamos a neutralizar si no esta
    el parámetro --no-neutralize entonces se hace la neutralizacion"""

    if not args.no_neutralize:
        print("The neutralization is Not implemented")
        exit()

    if not args.db_name:
        print("Missing --db-name argument")

    # Obtener el nombre del restore
    backup_filename = get_restore_filename(args)
    print(f"Backup {args.db_name} into file {backup_filename}")

    # Obtener acceso a postgres desde odoo.conf
    credentials = get_credentials(f"{args.base}/config/odoo.conf")

    # Crear un temp donde armar el backup
    with tempfile.TemporaryDirectory() as tempdir:
        # copiar el filestore a tempdir
        shutil.copytree(f"{args.base}/data_dir/filestore/{args.db_name}", f"{tempdir}/filestore")
        os.environ["PGPASSWORD"] = credentials['db_password']
        # Crear el dump
        try:
            cmd = [
                "pg_dump",
                f"--dbname={credentials['db_name']}",
                f"--host={credentials['db_host']}",
                f"--username={credentials['db_user']}",
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

def restore_database(args):
    if not args.db_name:
        print("Missing --db-name argument")

    try:
        # Crear conexion a la base de datos
        conn = psycopg2.connect(
            user="odoo",
            host="db",
            port=5432,
            password="odoo",
            dbname="postgres",
        )
    except Exception as ex:
        print('No se puede conectar a la BD esta el contenedor levantado?',str(ex))
        exit()

    # Obtener el nombre del backup
    backup_filename = get_backup_filename(args)
    print(f"Restoring {backup_filename} into Database {args.db_name}")

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    killing_db_connections(args, cur)
    drop_database(args, cur)
    create_database(args, cur)
    do_restore_database(args, backup_filename)

    rojo = "\033[91m"
    resetear_color = "\033[0m"

    if args.no_neutralize:
        print(
            f"{rojo}RESTORE TO {args.db_name} DATABASE IS FIHISHED , "
            f"WARNING - DATABASE IS NOT NEUTRALIZED - WARNING {resetear_color}"
        )
    else:
        neutralize_database(args, cur)
        print(f"RESTORE FIHISHED FOR {args.db_name}, " "DATABASE IS NEUTRALIZED")


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--base",
        default="/base",
        help="Proyect dir, (i.e. /odoo_ar/odoo-16.0e/bukito)",
    )
    arg_parser.add_argument(
        "--db_name",
        help="Database name to restore into or tu backup from",
    )
    arg_parser.add_argument(
        "--zipfile",
        help="The backup filename.\n"
        "On restore, defaults to the last backup file. "
        "On backup, defaults to a filename with a timestamp",
    )
    arg_parser.add_argument(
        "--days-to-keep",
        help="Number of days to keep backups"
    )
    arg_parser.add_argument(
        "--restore",
        action="store_true",
        help="Restore database",
    )
    arg_parser.add_argument(
        "--backup",
        action="store_true",
        help="Backup database",
    )
    arg_parser.add_argument(
        "--no-neutralize",
        action="store_true",
        help="Make an exact database (no neutralize)",
    )
    args = arg_parser.parse_args()
    if args.restore and args.backup:
        print("Yu must issue a backup or a restore command")
        exit()

    print("Database utils V1.4.1")
    print()

    if args.restore:
        restore_database(args)
    if args.backup:
        backup_database(args)
        cleanup_backup_files(args)
        print("database backed up")
