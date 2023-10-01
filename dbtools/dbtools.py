#!/usr/bin/env python3
#
# Script que se ejecuta al lanzar la imagen
#

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
    """Obtener el nombre del archivo hacia el cual backupear"""
    if args.zipfile:
        backup_filename = f"{args.base}/backup_dir/{args.zipfile}"
        # Verificar si el archivo existe y terminar con error
        if os.path.exists(backup_filename):
            print(f"The file {args.zipfile} already exists")
            exit()
    else:
        fecha_hora_actual = datetime.datetime.now(
            pytz.timezone("America/Argentina/Buenos_Aires")
        )
        zipfile = fecha_hora_actual.strftime("bkp_%Y-%m-%d_%H-%M-%S_GMT-3.zip")

    print(f"The new backup file is {zipfile}")
    return f"{args.base}/backup_dir/{zipfile}"


def get_backup_filename(args):
    """Obtener nombre del backup a restaurar"""

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
        print("Restoring filestore")
        # Iterate over all the files in the ZIP
        for file in zip_ref.namelist():
            # Check if the file is in the filestore folder
            if file.startswith("filestore"):
                # Extract the file to the filestore folder
                zip_ref.extract(member=file, path=filestorepath)

        print("extracting dump")
        # Extract the database dump to the temporary directory
        zip_ref.extract(member="dump.sql", path=tempdir)

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

    with tempfile.TemporaryDirectory() as tempdir:
        # Extraer el Filestore al filestore de la estructura y el backup al temp dir
        dump_filename = deflate_zip(args, backup_filename, tempdir)
        with open(dump_filename, "r") as d_filename:
            # Run psql command as a subprocess, and specify that the dump file should
            # be passed as standard input to the psql process
            os.environ["PGPASSWORD"] = "odoo"
            print("Restoring Database")
            process = subprocess.run(
                ["psql", "-U", "odoo", "-h", "db", "-d", "%s" % args.db_name],
                stdout=subprocess.PIPE,
                stdin=d_filename,
            )

        if int(process.returncode) != 0:
            print(f"The restored proces end with error {process.returncode}")
            exit(1)


def neutralize_database(args, cur):
    """Esto no funciona hay que rehacerlo"""
    print("neutralizando base de datos")
    with open("neutralize.sql") as _f:
        sql = _f.read()
    print(sql)
    cur.execute(sql)


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

    # Crear un temp donde armar el backup
    with tempfile.TemporaryDirectory() as tempdir:
        # copiar el filestore a tempdir
        shutil.copytree(f"{args.base}/data_dir/filestore", f"{tempdir}/filestore")
        os.environ["PGPASSWORD"] = "odoo"
        # Crear el dump
        try:
            cmd = [
                "pg_dump",
                f"--dbname={args.db_name}",
                f"--host=db",
                "--username=odoo",
                f"--file={tempdir}/dump.slq",
                "--no-owner",
            ]
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"error en backup {e}")
            exit()

        # zipear y mover al archivo destino
        shutil.make_archive(backup_filename, "zip", tempdir)


def restore_database(args):
    if not args.db_name:
        print("Missing --db-name argument")

    # Obtener el nombre del backup
    backup_filename = get_backup_filename(args)
    print(f"Restoring {backup_filename} into Database {args.db_name}")

    # Crear conexion a la base de datos
    conn = psycopg2.connect(
        user="odoo",
        host="db",
        port=5432,
        password="odoo",
        dbname="postgres",
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    killing_db_connections(args, cur)
    drop_database(args, cur)
    create_database(args, cur)
    do_restore_database(args, backup_filename)

    if args.no_neutralize:
        print(
            f"RESTORE TO {args.db_name} DATABASE IS FIHISHED , "
            "WARNING - DATABASE IS NOT NEUTRALIZED - WARNING"
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

    print("Database utils V1.4.0")
    print()

    if args.restore:
        restore_database(args)
    if args.backup:
        backup_database(args)
        print("database backed up")
