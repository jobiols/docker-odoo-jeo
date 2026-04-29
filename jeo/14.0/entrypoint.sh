#!/bin/bash
# Exit immediately if a command exits with a non-zero status.
set -e

echo "Odoo $ODOO_VERSION Release $ODOO_RELEASE by jeo Software"

# ---------------------------------------------------------------------------
# Database connection parameters
# Renamed to DB_HOST / DB_USER / DB_PASSWORD to avoid shadowing shell
# builtins ($HOST, $USER). Falls back to sane defaults if not set.
# Legacy --link variables (DB_PORT_5432_TCP_*) removed: use docker networks.
# ---------------------------------------------------------------------------
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-odoo}"
DB_PASSWORD="${DB_PASSWORD:-odoo}"

# ---------------------------------------------------------------------------
# Validate that ODOO_RC is set and the file exists before using it.
# ---------------------------------------------------------------------------
if [ -z "$ODOO_RC" ]; then
    echo "ERROR: ODOO_RC environment variable is not set." >&2
    exit 1
fi

if [ ! -f "$ODOO_RC" ]; then
    echo "ERROR: Odoo config file not found: $ODOO_RC" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Wait for Postgres to be ready.
# Uses a bounded retry loop instead of unbounded recursion.
# Timeout configurable via WAIT_DB_TIMEOUT (default 60 s).
# ---------------------------------------------------------------------------
WAIT_DB_TIMEOUT="${WAIT_DB_TIMEOUT:-60}"
WAITED=0

echo "Waiting for the database server at ${DB_HOST}:${DB_PORT} ..." >&2

until PGPASSWORD="$DB_PASSWORD" psql \
        --host="$DB_HOST" \
        --port="$DB_PORT" \
        --username="$DB_USER" \
        --list > /dev/null 2>&1
do
    if [ "$WAITED" -ge "$WAIT_DB_TIMEOUT" ]; then
        echo "ERROR: Database not available after ${WAIT_DB_TIMEOUT}s. Aborting." >&2
        exit 1
    fi
    echo "  ... still waiting (${WAITED}s elapsed)" >&2
    sleep 2
    WAITED=$((WAITED + 2))
done

echo "Database is ready." >&2

# ---------------------------------------------------------------------------
# Build extra CLI args for parameters not already present in ODOO_RC.
# ---------------------------------------------------------------------------
DB_ARGS=()

check_config() {
    local param="$1"
    local value="$2"
    if ! grep -qE "^\s*\b${param}\b\s*=" "$ODOO_RC"; then
        DB_ARGS+=("--${param}" "${value}")
    fi
}

check_config "db_host"     "$DB_HOST"
check_config "db_port"     "$DB_PORT"
check_config "db_user"     "$DB_USER"
check_config "db_password" "$DB_PASSWORD"

# ---------------------------------------------------------------------------
# Graceful shutdown: forward SIGTERM to the Odoo child process.
# ---------------------------------------------------------------------------
_shutdown() {
    if [ -n "$ODOO_PID" ]; then
        echo "Caught SIGTERM — shutting down Odoo (PID $ODOO_PID)..." >&2
        kill -SIGTERM "$ODOO_PID"
        wait "$ODOO_PID"
    fi
}
trap _shutdown SIGTERM SIGINT

# ---------------------------------------------------------------------------
# Main dispatch
# ---------------------------------------------------------------------------
case "$1" in
    -- | odoo)
        shift
        if [ "$1" = "scaffold" ]; then
            exec odoo "$@"
        else
            exec odoo "$@" "${DB_ARGS[@]}"
        fi
        ;;
    -*)
        # Flags passed directly (e.g. -c /etc/odoo/odoo.conf -u all)
        exec odoo "$@" "${DB_ARGS[@]}"
        ;;
    "")
        # No arguments: launch Odoo with defaults
        exec odoo "${DB_ARGS[@]}"
        ;;
    *)
        # Arbitrary command (e.g. bash, python, etc.)
        exec "$@"
        ;;
esac