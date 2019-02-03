#!/usr/bin/env bash

if [ -d /backup/tmp ]
  then
    rm -r /backup/tmp -f
fi

unzip -d /backup/tmp /backup/${ZIPFILE}

if [ -d /backup/tmp/filestore ]
  then
    echo "Restoring files."
    rm -r /filestore/${NEW_DBNAME} -f
    mkdir /filestore/${NEW_DBNAME}
    cp -r /backup/tmp/filestore/* /filestore/${NEW_DBNAME}/
    chmod -R o+w /filestore/${NEW_DBNAME}/
    if [ $? -ne 0 ]
      then
        echo "Error! Restore of files failed!"
        exit 2
    fi
    echo "Files restored"
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

rm -r /backup/tmp

if [ $? -ne 0 ]
  then
    echo "Error! DB restore failed!"
    exit 2
fi
echo "Restore finished"
