#!/usr/bin/env bash
#
# Script par hacer Build de las imagnes enterprise solo local
# Baja los fuentes enterprise de vauxoo de cada version y los pone en este
# repositorio luego hace un make de cada version.
#
# Finalmente hay que hacer un push a github para que se haga el build en
# dockerhub, hacerlo manual porque el vscode se tara con tantos archivos.
CD="/home/jobiols/git-repos/docker-odoo-jeo/jeo"

versions=( 11.0 12.0 13.0 14.0 )

for version in ${versions[@]}
do 
    echo "********************************************************************"   
    echo "Building V$version"

    # moverse al directorio correspondiente
    cd "$CD/$version"
    if ! ./make.sh;
    then
        echo "Failed jobiols/odoo-jeo:$version"
        exit 1
    else
        echo "----------> Success jobiols/odoo-jeo:$version"
        echo
    fi
    cd "$CD/$version".debug

    if ! ./make.sh;
    then
        echo "Failed jobiols/odoo-jeo:$version.debug"
        exit 1
    else
        echo "----------> Success jobiols/odoo-jeo:$version.debug"
        echo
    fi

done