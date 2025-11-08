#!/usr/bin/env bash
sd build --no-cache --pull --rm=true -t jobiols/odoo-jeo:19.0.debug ./
result=$?
if [ "$result" -eq 0 ]; then
    sd push jobiols/odoo-jeo:19.0.debug
else
    echo "Falló la creación de la imagen"
fi
exit $result
