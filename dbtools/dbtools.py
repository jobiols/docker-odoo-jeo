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
from zipfile import ZipFile
import shutil

def get_backup_filename(args):
    # Obtener el backup a restaurar
    print('Get Backup Filename')
    if args.zipfile:
        backup_filename = f"/{args.base}/backup_dir/{args.zipfile}"
        print(backup_filename)
        print("The selected backup is " + backup_filename)
        return backup_filename
    else:
        files = glob.glob("%s/backup_dir/*.zip" % args.base)
        if files:
            backup_filename = max(files, key=os.path.getctime)
            print("The latest backup is %s" % os.path.basename(backup_filename))
            return backup_filename
        else:
            print("No backups to restore !")
            exit()

def deflate_zip(args, backup_filename, tempdir):
    """ Unpack backup and filestore """

    # Path to the filestore folder
    filestorepath = "%s/data_dir/filestore/%s" % (args.base, args.db_name)

    # If the filestore folder already exists, delete it
    if os.path.exists(filestorepath):
        shutil.rmtree(filestorepath)

    # Open the ZIP file
    with ZipFile(backup_filename, "r") as zip_ref:
        print('Restoring filestore')
        # Iterate over all the files in the ZIP
        for file in zip_ref.namelist():
            # Check if the file is in the filestore folder
            if file.startswith('filestore'):
                # Extract the file to the filestore folder
                zip_ref.extract(member=file, path=filestorepath)

        print('extracting dump')
        # Extract the database dump to the temporary directory
        zip_ref.extract(member="dump.sql", path=tempdir)

    # Return the full path to the database dump file in the temporary directory
    return tempdir + '/dump.sql'

def killing_db_connections(args, cur):
    print(f"Killing backend connections to {args.db_name}")
    sql = (""" SELECT pg_terminate_backend(pid) FROM pg_stat_activity
               WHERE datname = '%s';
        """ % args.db_name
    )
    cur.execute(sql)

def drop_database(args, cur):
    sql = f"DROP DATABASE IF EXISTS {args.db_name};"
    cur.execute(sql)

def create_database(args, cur):
    sql = f"CREATE DATABASE {args.db_name};"
    cur.execute(sql)

def do_restore_database(args, backup_filename):
    """ Restore database and filestore """

    with tempfile.TemporaryDirectory() as tempdir:
        # Extraer el Filestore al filestore de la estructura y el backup al temp dir
        dump_filename = deflate_zip(args, backup_filename, tempdir)
        with open(dump_filename, 'r') as d_filename:
            # Run psql command as a subprocess, and specify that the dump file should
            # be passed as standard input to the psql process
            os.environ["PGPASSWORD"] = 'odoo'
            process = subprocess.run(
                ['psql',
                '-U','odoo',
                '-h','db',
                '-d','%s' % args.db_name],
                stdout=subprocess.PIPE,
                stdin=d_filename
            )

        if int(process.returncode) != 0:
            print(f'The restored proces end with error {process.returncode}')
            exit(1)

def deactivate_database(args, cur):
    with open('deactivate.sql') as _f:
        sql = _f.readlines()
    cur.execute(sql)

def restore_database(args):
    """ Restore database """
    print(f'Restoring Database "{args.db_name}"')

    if not args.db_name:
        print("missing --db-name argument")

    # Obtener el nombre del backup
    backup_filename = get_backup_filename(args)

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
    drop_database(args,cur)
    create_database(args, cur)

    do_restore_database(args, backup_filename)

    if args.deactivate:
        deactivate_database(args)
        print("RESTORE FIHISHED DATABASE %s IS DEACTIVATED" % args.db_name)
    else:
        print("RESTORE FIHISHED FOR %s WARNING, DATABASE IS --NOT-- DEACTIVATED" % args.db_name)

if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--base", default="/base", help='Base dir')
    arg_parser.add_argument("--db_name", help='Database Name')
    arg_parser.add_argument("--zipfile", help='Zip file with odoo database')
    arg_parser.add_argument("--restore", action="store_true")
    arg_parser.add_argument("--deactivate", action="store_true")
    args = arg_parser.parse_args()

    print('Restore Database V1.4.0')
    if args.restore:
        restore_database(args)
