#!/usr/bin/env bash

set -e

# eliminar el directorio /backup/temp si es que existe
rm -rf /backup/tmp

# si zipfile esta vacio busco el ultimo
if [[ -z "${ZIPFILE}" ]]; then
    echo "Searching for latest backup"
    unset -v latest
    for file in "/backup"/*; do
      [[ $file -nt $latest ]] && ZIPFILE=$file
    done
    echo "Latest file is $ZIPFILE"
else
    ZIPFILE="/backup/$ZIPFILE"
fi

unzip -q -d /backup/tmp ${ZIPFILE}

if [ -d /backup/tmp/filestore ]
  then
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
fi

if [ ! -f /backup/tmp/dump.sql ]
  then
    echo "Error! dump file not found!"
    exit 2
fi

export PGPASSWORD="odoo"

echo "create empty database ${NEW_DBNAME}"
createdb -U odoo -h db -T template0 ${NEW_DBNAME}

echo "restore to new created database"
psql -U odoo -h db -d ${NEW_DBNAME} -q < /backup/tmp/dump.sql >/dev/null

rm -rf /backup/tmp

echo "--------------------"
echo "  Restore finished  "
echo "--------------------"
