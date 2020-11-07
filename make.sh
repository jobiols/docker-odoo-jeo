#!/usr/bin/env bash
#
# Script par hacer Build de las imagenes community

CD="/home/jobiols/git-repos/docker-odoo-jeo/jeo"

versions=( 11.0 12.0 13.0 14.0 )

for version in ${versions[@]}
do 
    echo "******************************************************************** Building V$version" 
    echo

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
