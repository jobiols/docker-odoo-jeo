#!/bin/sh
# Testear la imagen

# backup normal
sudo docker run --rm -i \
    --link pg-potenciar13:db \
    -v /odoo/ar/odoo-13.0/potenciar13/:/base \
    jobiols/dbtools:1.4.0 --restore --help
