#!/usr/bin/env bash
sd build --rm=true -t jobiols/odoo-jeo:17.1 ./
result=$?
if [ "$result" -eq 0 ]; then
    sd push jobiols/odoo-jeo:17.1
else
    echo "Falló la creación de la imagen"
fi
exit $result
