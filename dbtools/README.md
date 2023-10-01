Docker image with posgres tools to manage backup and restore


sudo docker run --rm -i \
    --link postgres_image:db \
    -v base_path:/base \
    jobiols/dbtools:1.4.0 --db_name bukito_prod --zipfile bk.zip --restore

- postgres_image: image name for postgres server
- base_path: path to base dir of the project
- --db_name: Nombre del la base de datos
- --zipfile: Nombre del archivo zip con la BD
- --restore: accion de restaurar
