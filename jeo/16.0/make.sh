#!/usr/bin/env bash
sudo docker build --build-arg ODOO_RELEASE=$(date +%Y%m%d) --tag jobiols/odoo-jeo:16.0 ./
result=$?
if [ "$result" -eq 0 ]; then
    sd push jobiols/odoo-jeo:16.0
else
    echo "Falló la creación de la imagen"
fi
exit $result
