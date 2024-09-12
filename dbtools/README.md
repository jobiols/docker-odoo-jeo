Docker image with posgres tools to manage backup and restore

    #!/bin/bash
    # --------------------------------------------------------------------------------------
    # Hacer un backup de la base de produccion
    # --------------------------------------------------------------------------------------
    sudo docker run --rm -i \
        --network compose_default \
        --volume /odoo_ar/odoo-16.0e/lopez:/base \
        jobiols/dbtools:1.4.1 \
            --db_name lopez_prod \
            --no-neutralize \
            --days-to-keep 3 \
            --backup


    #!/bin/bash
    # --------------------------------------------------------------------------------------
    # Hacer un restore de la base de produccion
    # --------------------------------------------------------------------------------------
    sudo docker run --rm -i \
        --network compose_default \
        --volume /odoo_ar/odoo-16.0e/lopez:/base \
        jobiols/dbtools:1.4.1 \
            --db_name lopez_prod \
            --no-neutralize \
            --restore

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
