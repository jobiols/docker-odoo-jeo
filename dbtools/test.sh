#!/bin/sh
# Testear la imagen

# Seria interesante hacer un backup y un restore con pg_backup pg_restore porque tienen
# capacidad de usar multiples cores
#sd build --rm=true -t jobiols/dbtools:1.4.1 ./

echo "iniciando Test"
echo

# backup normal
# sudo docker run --rm -i \
#     --link pg-bukito:db \
#     -v /odoo/ar/odoo-16.0e/bukito:/base \
#     jobiols/dbtools:1.4.1 \
#     --db-name bukito_prod \
#     --backup

# restore normal
sudo docker run --rm -i \
    --link pg-villandry16:db \
    -v /odoo/ar/odoo-16.0e/villandry16:/base \
    jobiols/dbtools:1.5.0 \
    --db-name villandry_prod \
    --restore \
    --project cl-villandry/villandry16_default
