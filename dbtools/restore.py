#!/usr/bin/env python3
#
# Script que se ejecuta al lanzar la imagen
#
import argparse
from asyncio import subprocess
import tempfile
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os, glob
from zipfile import ZipFile

def get_backup_filename(args):
    # Obtener el backup a restaurar
    if args.zipfile:
        backup_filename = "%s/backup_dir/%s" % (args.base, args.zipfile)
        print("The selected backup is " + backup_filename)
        return backup_filename
    else:
        files = glob.glob("%s/backup_dir/*.zip" % args.base)
        if files:
            backup_filename = max(files, key=os.path.getctime)
            print("The latest backup is %s" % backup_filename)
            return backup_filename
        else:
            print("No backups to restore !")
            exit()

def deflate_zip(args, backup_filename):
    filestorepath = "%s/data_dir/filestore/%s" % (args.base, args.db_name)
    tempdir = tempfile.TemporaryDirectory()
    os.rmdir(filestorepath)
    os.mkdirs(filestorepath)
    with ZipFile(backup_filename, "r") as zip_ref:
        print('restoring filestore')
        zip_ref.extract(member="filestore", path=filestorepath)
        print('extracting dump')
        zip_ref.extract(member="dump.sql", path=tempdir)
    return tempdir + 'dump.sql'

def killing_db_connections(args, cur):
    print("Killing backend connections to %s" % args.db_name)
    sql = (""" SELECT pg_terminate_backend(pid) FROM pg_stat_activity
               WHERE datname = %s;
        """ % args.db_name
    )
    cur.execute(sql)

def test_exists_database(args, cur):
    print("Testing if database %s exists" % args.db_name)
    sql = """SELECT EXISTS(SELECT RELNAME FROM pg_class
                    WHERE RELNAME = %s AND RELKIND = 'r');
    """ % args.db_name
    cur.execute(sql)
    return cur.fetchone()[0]

def drop_database(args, cur):
    sql = "DROP DATABASE %s;" % args.db_name
    cur.execute(sql)

def create_database(args, cur):
    sql = "CREATE DATABASE %s;" % args.db_name
    cur.execute(sql)

def restore_database(args, dump_filename):
    process = subprocess.Popen(
        ['pg_restore',
        '--no-owner',
        '--dbname=postgresql://%s:%s@%s:%s/%s' % ('odoo','odoo','db',5432,args.db_name),
        '-v',
        '%s/dump.sql' % (dump_filename)],
        stdout=subprocess.PIPE
    )
    output = process.communicate()[0]
    if int(process.returncode) != 0:
        print('Falla')

def deactivate_database(args, cur):
    with open('deactivate.sql') as _f:
        sql = _f.readlines()
    cur.execute(sql)

def restore_database(args):
    if not args.db_name:
        print("missing --db-name argument")

    if not args.base:
        print("missing --base argument")

    # Obtener el nombre del backup
    backup_filename = get_backup_filename(args)

    # Extraer el Filestore y el backup
    dump_filename = deflate_zip(args, backup_filename)

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
    if test_exists_database(args,cur):
        drop_database(args,cur)
    create_database(args, cur)
    restore_database(args, dump_filename)

    if args.deactivate:
        deactivate_database(args)
        print("RESTORE FIHISHED DATABASE %s IS DEACTIVATED" % args.db_name)
    else:
        print("RESTORE FIHISHED FOR %s WARNING, DATABASE IS --NOT-- DEACTIVATED" % args.db_name)

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--base")
    arg_parser.add_argument("--db_name")
    arg_parser.add_argument("--zipfile")
    arg_parser.add_argument("--restore", action="store_true")
    arg_parser.add_argument("--drop-db", action="store_true")
    arg_parser.add_argument("--deactivate", action="store_true")
    args = arg_parser.parse_args()

    if args.restore:
        restore_database(args)
