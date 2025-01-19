#!/bin/sh
# Testear la imagen

# Seria interesante hacer un backup y un restore con pg_backup pg_restore porque tienen
# capacidad de usar multiples cores
sd build --rm=true -t jobiols/dbtools:1.4.6 ./


# restore normal
# sudo docker run --rm -it \
#     --link pg-maverick:db \
#     -v /odoo/ar/odoo-16.0e/maverick:/base \
#     jobiols/dbtools:1.4.4 --db-name maverick_prod \
#     --days-to-keep 3 \
#     --restore

echo "BACKUP\n"
# backup normal
sudo docker run --rm \
    --link pg-bukito:db \
    -v /odoo/ar/odoo-16.0e/bukito:/base \
    jobiols/dbtools:1.4.6 \
    --backup

echo "RESTORE\n"
# restore normal
sudo docker run --rm \
    --link pg-bukito:db \
    -v /odoo/ar/odoo-16.0e/bukito:/base \
    jobiols/dbtools:1.4.6 \
    --restore
