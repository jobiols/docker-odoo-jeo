#!/bin/bash

# exit inmediately if a command exits with a non-zero status.
set -e

echo "Odoo $ODOO_VERSION Release $ODOO_RELEASE by jeo Software"

# set the postgres database host, port, user and password according to the environment
# and pass them as arguments to the odoo process if not present in the config file
: ${HOST:=${DB_PORT_5432_TCP_ADDR:='db'}}
: ${PORT:=${DB_PORT_5432_TCP_PORT:=5432}}
: ${USER:=${DB_ENV_POSTGRES_USER:=${POSTGRES_USER:='odoo'}}}
: ${PASSWORD:=${DB_ENV_POSTGRES_PASSWORD:=${POSTGRES_PASSWORD:='odoo'}}}

# Know if Postgres is listening
function db_is_listening() {
    psql --list > /dev/null 2>&1 || (sleep 1 && db_is_listening)
}

echo Waiting until the database server is listening... > /dev/stderr
#db_is_listening

# Check pg user exist
function pg_user_exist() {
    psql postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$PGUSER'" > /dev/null 2>&1 || (sleep 1 && pg_user_exist)
}

echo Waiting until the pg user $PGUSER is created... > /dev/stderr
#pg_user_exist

# Add the unaccent module for the database if needed
echo Trying to install unaccent extension... > /dev/stderr
#psql -d $DB_TEMPLATE -c 'CREATE EXTENSION IF NOT EXISTS unaccent;'

DB_ARGS=()
function check_config() {
    param="$1"
    value="$2"
    if ! grep -q -E "^\s*\b${param}\b\s*=" "$ODOO_RC" ; then
        DB_ARGS+=("--${param}")
        DB_ARGS+=("${value}")
   fi;
}
check_config "db_host" "$HOST"
check_config "db_port" "$PORT"
check_config "db_user" "$USER"
check_config "db_password" "$PASSWORD"

case "$1" in
    -- | odoo)
        shift
        if [[ "$1" == "scaffold" ]] ; then
            exec odoo "$@"
        else
            exec odoo "$@" "${DB_ARGS[@]}"
        fi
        ;;
    -*)
        exec odoo "$@" "${DB_ARGS[@]}"
        ;;
    *)
        exec "$@"
esac

exit 1
