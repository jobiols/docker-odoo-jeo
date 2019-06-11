#!/usr/bin/env bash
# este script corre dentro de la imagen

set -e

echo "EXTEND DATABASE LICENSE ${NEW_DBNAME}
psql -U odoo -h db -d ${NEW_DBNAME} -q < /extend.sql
echo "RESTORE FIHISHED DATABASE ${NEW_DBNAME} IS DEACTIVATED"
