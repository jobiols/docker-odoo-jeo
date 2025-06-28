#!/usr/bin/env bash
#sd build --rm=true --no-cache -t jobiols/odoo-jeo:16.01 ./
sudo docker build --build-arg ODOO_RELEASE=$(date +%Y%m%d) --tag jobiols/odoo-jeo:16.01 ./
result=$?
if [ "$result" -eq 0 ]; then
    sd push jobiols/odoo-jeo:16.01
else
    echo "Falló la creación de la imagen"
fi
exit $result
