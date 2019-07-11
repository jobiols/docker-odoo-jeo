#!/usr/bin/env bash
set -e

export PGPASSWORD="odoo"
psql -U odoo -h db -d ${NEW_DBNAME} -q < /extend.sql
