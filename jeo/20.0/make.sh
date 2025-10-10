#!/usr/bin/env bash
sudo docker build --rm=true --build-arg ODOO_RELEASE=$(date -u +%Y%m%d) -t jobiols/odoo-jeo:20.0 ./
result=$?
if [ "$result" -eq 0 ]; then
    sd push jobiols/odoo-jeo:20.0
else
    echo "Falló la creación de la imagen"
fi
exit $result
