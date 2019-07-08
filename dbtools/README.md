Imagen docker con las herramientas de postgres para restaurar un backup

uso:

sudo docker run --rm -i \
    --link postgres_image:db \
    -v path_al_filestore:/filestore \
    -v path_al_backup/:/backup \
    --env NEW_DBNAME=database_name \
    --env ZIPFILE=backup_a_restaurar \
    --env DEACTIVATE=True \
    jobiols/dbtools

- postgres_image: nombre de la imagen donde esta el servidor postgres
- path_al_filestore: ubicacion del filestore a restaurar
- path_al_backup: ubicacion del archivo de backup a restaurar
- NEW_DBNAME: nombre de la base a restaurar, si existe la borra, si esta abierta por otras aplicaciones mata las conexiones
- ZIPFILE: nombre del bakcup a restaurar, si no esta, se trae el mas nuevo
- DEACTIVATE = True entonces corre el script de desactivacion, si no esta (no vale ponerlo en false, no tiene que estar), no la desactiva
