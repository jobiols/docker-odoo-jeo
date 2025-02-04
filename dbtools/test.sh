#!/bin/sh
# Testear la imagen

# Seria interesante hacer un backup y un restore con pg_backup pg_restore porque tienen
# capacidad de usar multiples cores
sd build --rm=true -t jobiols/dbtools:1.4.7 ./


# restore normal
# sudo docker run --rm -it \
#     --link pg-maverick:db \
#     -v /odoo/ar/odoo-16.0e/maverick:/base \
#     jobiols/dbtools:1.4.4 --db-name maverick_prod \
#     --days-to-keep 3 \
#     --restore

base=/odoo/ar/odoo-16.0e/bukito
link=pg-bukito:db
dbtools=jobiols/dbtools:1.4.7


echo "BACKUP\n"
# backup normal
sudo docker run --rm \
    --link $link \
    -v $base:/base \
    $dbtools \
    --backup

echo "BACKUP x 10 dias\n"
# backup normal
sudo docker run --rm \
    --link $link \
    -v $base:/base \
    $dbtools \
    --days-to-keep 10 \
    --backup

echo "RESTORE\n"
# restore normal
sudo docker run --rm \
    --link $link \
    -v $base:/base \
    $dbtools \
    --restore
