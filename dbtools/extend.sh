#!/bin/ash
# este script corre dentro de la imagen

export PGPASSWORD="odoo"
psql -U odoo -h db -d ${NEW_DBNAME} -q < /extend.sql
