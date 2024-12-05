#!/bin/sh
# Testear la imagen

# Seria interesante hacer un backup y un restore con pg_backup pg_restore porque tienen
# capacidad de usar multiples cores
sd build --rm=true -t jobiols/dbtools:1.4.3 ./

echo "iniciando Test"
echo

# restore normal
# sudo docker run --rm -it \
#     --link pg-maverick:db \
#     -v /odoo/ar/odoo-16.0e/maverick:/base \
#     jobiols/dbtools:1.4.3 --db-name maverick_prod \
#     --days-to-keep 3 \
#     --restore

# backup normal
sudo docker run --rm -it \
    --link pg-lopez:db \
    -v /odoo/ar/odoo-16.0e/lopez:/base \
    jobiols/dbtools:1.4.3 --db-name lopez_prod \
    --backup
