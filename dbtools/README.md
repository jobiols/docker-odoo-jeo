Docker image with posgres tools to manage backup and restore

    sudo docker run --rm -i \
        --link postgres_image:db \
        -v base_path:/base \
        jobiols/dbtools:1.4.0 \
            --db_name bukito_prod \
            --backup

    optional arguments:
    -h, --help         show this help message and exit
    --base BASE        Proyect dir, (i.e. /odoo_ar/odoo-16.0e/bukito)
    --db_name DB_NAME  Database name to restore into or tu backup from
    --zipfile ZIPFILE  The backup filename. On restore, defaults to the last
                        backup file. On backup, defaults to a filename with a
                        timestamp
    --restore          Restore database
    --backup           Backup database
    --no-neutralize    Make an exact database (no neutralize)
