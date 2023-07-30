#!/bin/sh
# Testear la imagen

# Seria interesante hacer un backup y un restore con pg_backup pg_restore porque tienen
# capacidad de usar multiples cores

# backup normal
sudo docker run --rm -i \
    --link pg-bukito:db \
    -v /odoo/ar/odoo-16.0e/bukito:/base \
    jobiols/dbtools:1.4.0  --db_name bukito_prod --zipfile bk.zip --restore

