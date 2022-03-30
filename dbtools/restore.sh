#!/bin/bash
# este script corre dentro de la imagen

# eliminar el directorio /backup/temp si es que existe
rm -rf /backup/tmp

# si el parametro zipfile esta vacio busco el ultimo backup
if [[ -z "${ZIPFILE}" ]]; then
    ZIPFILE=$(ls /backup/*.zip -t | head -1)
    echo "Latest file is $ZIPFILE"
else
    ZIPFILE="/backup/$ZIPFILE"
    echo "The selected file is $ZIPFILE"
fi

unzip -q -d /backup/tmp ${ZIPFILE}

if [ -d /backup/tmp/filestore ]
  then
    echo "Restoring filestore"
    rm -rf /filestore/${NEW_DBNAME}
    mkdir /filestore/${NEW_DBNAME}
    cp -r /backup/tmp/filestore/* /filestore/${NEW_DBNAME}/
    chmod -R o+w /filestore/${NEW_DBNAME}/
    if [ $? -ne 0 ]
      then
        echo "Error! Restore of files failed!"
        exit 2
    fi
    echo "Filestore restored succesfully"
    echo
fi

if [ ! -f /backup/tmp/dump.sql ]
  then
    echo "Error! dump file not found!"
    exit 2
fi

export PGPASSWORD="odoo"

sql="SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${NEW_DBNAME}';"
echo "Killing backend connections to ${NEW_DBNAME}"
if psql -U odoo -h db -d postgres -c "$sql"
then
    echo "Connection is clean"
    echo
fi

echo "Testing if database ${NEW_DBNAME} exists"
if psql -U odoo -h db -lqt | cut -d \| -f 1 | grep -qw ${NEW_DBNAME}
then
    echo "Droping database ${NEW_DBNAME}"
    dropdb -U odoo -h db ${NEW_DBNAME}
fi

echo "Create empty database ${NEW_DBNAME}"
createdb -U odoo -h db -T template0 ${NEW_DBNAME}

echo "Restoring to new created database"
psql -U odoo -h db -d ${NEW_DBNAME} -q < /backup/tmp/dump.sql >/dev/null

# si estoy en desarrollo desactivo la BD
if [[ -z "$DEACTIVATE" ]]
then
    echo "RESTORE FIHISHED FOR ${NEW_DBNAME} WARNING, DATABASE IS --NOT-- DEACTIVATED"
else
    psql -U odoo -h db -d ${NEW_DBNAME} -q < /deactivate.sql
    echo "RESTORE FIHISHED DATABASE ${NEW_DBNAME} IS DEACTIVATED"
fi

# eliminar el directorio /backup/temp
rm -rf /backup/tmp
