Imagen docker con las herramientas de postgres para restaurar un backup

uso:

sudo docker run --rm -i \
    --link postgres_image:db \
    -v path_al_filestore:/filestore \
    --env NEW_DBNAME=database_name \
    --env DEACTIVATE=True \
    --env ZIPFILE=backup_a_restaurar
    jobiols/dbtools

- postgres_image: nombre de la imagen donde esta el servidor postgres
- path_al_filestore: ubicacion del filestore a restaurar
- NEW_DBNAME: nombre de la base a restaurar, si existe la borra pero no debe estar abierta por otras aplicaciones
- ZIPFILE: nombre del bakcup a restaurar, si no esta, se trae el mas nuevo
- DEACTIVATE = True entonces corre el script de desactivacion, si no esta (no vale ponerlo en false, no tiene que estar), no la desactiva
