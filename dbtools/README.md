Docker image whit posgres tools to manage backup and restore


sudo docker run --rm -i \
    --link postgres_image:db \
    -v base_path:/base \
    jobiols/dbtools:1.4.0 --help

- postgres_image: image name for postgres server
- base_path: path to base dir
- use --help to get help
