Docker image with posgres tools to manage backup and restore

    #!/bin/bash
    # --------------------------------------------------------------------------------------
    # Hacer un backup exacto de la base de produccion por defecto
    # El backup se guarda en BASE/backup_dir y se retienen los 3 ultimos días
    # --------------------------------------------------------------------------------------
    BASE="/odoo_ar/odoo-16.0e/lopez"
    sudo docker run --rm -i \
        --network compose_default \
        --volume ${BASE}:/base \
        jobiols/dbtools:1.4.1 \
            --days-to-keep 3 \
            --backup

    #!/bin/bash
    # --------------------------------------------------------------------------------------
    # Hacer un backup exacto de la base my_database
    # El backup se guarda en BASE/backup_dir y se retienen los 3 ultimos días
    # --------------------------------------------------------------------------------------
    BASE="/odoo_ar/odoo-16.0e/lopez"
    sudo docker run --rm -i \
        --network compose_default \
        --volume ${BASE}:/base \
        jobiols/dbtools:1.4.1 \
            --db-name my_database \
            --days-to-keep 3 \
            --backup

    # --------------------------------------------------------------------------------------
    # Hacer un backup exacto de la base my_database
    # El backup se guarda en BASE/backup_dir no se borra ningun backup antiguo
    # El nombre del archivo de restore es my_backup
    # --------------------------------------------------------------------------------------
    BASE="/odoo_ar/odoo-16.0e/lopez"
    sudo docker run --rm -i \
        --network compose_default \
        --volume ${BASE}:/base \
        jobiols/dbtools:1.4.1 \
            --db-name my_database
            --zipfile my_backup
            --backup

    #!/bin/bash
    # --------------------------------------------------------------------------------------
    # Hacer un restore exacto de la base de produccion el archivo de backup se toma
    # de BASE/backup_dir buscando el archivo más nuevo, el nobre de la BD a restaurar
    # es el default, el restore es exacto sin neutralización.
    # --------------------------------------------------------------------------------------
    BASE="/odoo_ar/odoo-16.0e/lopez"
    sudo docker run --rm -i \
        --network compose_default \
        --volume ${BASE}:/base \
        jobiols/dbtools:1.4.1 \
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
