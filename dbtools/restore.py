#!/usr/bin/env python3
#
# Script que se ejecuta al lanzar la imagen
#
import argparse
import psycopg2
import sys
import time
import os, glob
from zipfile import ZipFile

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--db_name')
    arg_parser.add_argument('--drop-db')
    arg_parser.add_argument('--zipfile')
    arg_parser.add_argument('--restore')
    arg_parser.add_argument('--deactivate')

args = arg_parser.parse_args()
# restore la BD
# drop DB if exists
# Get last file or zipfile if given

if args.restore:
    # Obtener el backup a restaurar
    if args.zipfile:
        backup_filename = args.zipfile
        print('The selected backup is ' + backup_filename)
    else:
        files = glob.glob('/backup/*.zip')
        backup_filename = max(files, key=os.path.getctime)
        print('The latest backup is '+ backup_filename)

    # Extraer el Filestore
    print('Restoring filestore...')
    os.rmdir('/filestore/' + args.db_name)
    os.mkdirs('/filestore/' + args.db_name)
    with ZipFile(backup_filename, 'r') as zip_ref:
        zip_ref.extract(member='filestore',path="/filestore/")

    # Eliminar la base de datos
    
