#!/bin/bash

set -e
echo "Odoo $ODOO_VERSION Release $ODOO_RELEASE by jeo Software"

# set the postgres database host, port, user and password according to the odoo.conf
# if not present in config file set defaults

# WARNING: the parameters in odoo.conf must habe spaces surrondnig the equal sign
# i.e. db_host = myhost GOOD
# i.e. db_host=myhost BAD

# Defaults, taken if parameters not found in odoo.conf
HOST='db'
PORT=5432
POSTGRES_USER='odoo'
POSTGRES_PASSWORD='odoo'

DB_ARGS=()
function check_config() {
    DB_ARGS+=("--$1")
    # Find the line starting with $1 and get the string after equal sign
    TMP=$(grep -E "^$1.*=" $ODOO_RC | awk '{print $3}')
    # Apply defaults if the parameter is not found in odoo.conf
    if [ -z $TMP ]; then
        if [ $1 == "db_host" ]; then
            DB_ARGS+=($HOST)
        fi
        if [ $1 == "db_port" ]; then
            DB_ARGS+=($PORT)
        fi
        if [ $1 == "db_user" ]; then
            DB_ARGS+=($POSTGRES_USER)
        fi
        if [ $1 == "db_password" ]; then
            DB_ARGS+=($POSTGRES_PASSWORD)
        fi
    else
        DB_ARGS+=($TMP)
    fi
}
check_config "db_host"
check_config "db_port"
check_config "db_user"
check_config "db_password"

case "$1" in
    -- | odoo)
        shift
        if [[ "$1" == "scaffold" ]] ; then
            exec odoo "$@"
        else
            wait-for-psql.py ${DB_ARGS[@]} --timeout=30
            exec odoo "$@" "${DB_ARGS[@]}"
        fi
        ;;
    -*)
        wait-for-psql.py ${DB_ARGS[@]} --timeout=30
        exec odoo "$@" "${DB_ARGS[@]}"
        ;;
    *)
        exec "$@"
esac

exit 1
