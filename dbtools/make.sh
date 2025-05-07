#!/usr/bin/env bash
sd build --no-cache --rm=true -t jobiols/dbtools:1.4.8 ./

result=$?
if [ "$result" -eq 0 ]; then
    sd push jobiols/dbtools:1.4.8
else
    echo "Falló la creación de la imagen"
fi
exit $return_code
