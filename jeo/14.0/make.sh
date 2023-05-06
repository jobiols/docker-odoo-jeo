#!/usr/bin/env bash
sd build --rm=true -t jobiols/odoo-jeo:14.0 ./
result=$?
if [ "$result" -eq 0 ]; then

    sd push jobiols/odoo-jeo:14.0
else
    echo "Falló la creación de la imagen"
fi
exit $return_code
