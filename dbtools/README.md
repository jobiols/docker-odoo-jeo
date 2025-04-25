Docker image with posgres tools to manage backup and restore

    #!/bin/bash
    # --------------------------------------------------------------------------------------
    # Hacer un backup de la base de produccion por defecto ([client]_default)
    # El backup se guarda en BASE/backup_dir se mantienen 3 dias
    # El archivo zip se guarda en BASE/backup_dir
    # si se hace con oe cambiar --network compose_default por --link pg-[client]:db
    # Si no se quiere borrar ningun backup omitir --days-to-keep
    # --------------------------------------------------------------------------------------
    base="/odoo_ar/odoo-16.0e/lopez"

    sudo docker run --rm -it \
        --volume ${base}:/base \
        --network compose_default
        -u $(stat -c '%u:%g' ${base}) \
        --link postgres:db \
        jobiols/dbtools:1.4.8 \
        --days-to-keep 3 \
        --backup

    #!/bin/bash
    # --------------------------------------------------------------------------------------
    # Hacer un restore de la base de produccion el archivo de backup se toma
    # de BASE/backup_dir buscando el archivo más nuevo, el nombre de la BD a restaurar
    # es el default a menos que esté el parametro --db-name
    # --------------------------------------------------------------------------------------
    BASE="/odoo_ar/odoo-16.0e/lopez"
    db_name=rubi_test_1209

    sudo docker run --rm -it \
        --volume ${base}:/base \
        --network compose_default
        -u $(stat -c '%u:%g' ${base}) \
        --link postgres:db \
        jobiols/dbtools:1.4.8 \
        --db-name $db_name \
        --restore
