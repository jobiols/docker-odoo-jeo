#!/usr/bin/env bash
sd build --rm=true -t jobiols/dbtools:1.4.3 ./

result=$?
if [ "$result" -eq 0 ]; then
    sd push jobiols/dbtools:1.4.3
else
    echo "Falló la creación de la imagen"
fi
exit $return_code
