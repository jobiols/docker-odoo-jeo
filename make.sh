#!/usr/bin/env bash
#
# Script par hacer Build de las imagenes community

set -e

# limpiar las copias de debug
cd /odoo/ar/odoo-16.0/
sudo rm -rf dist-local-packages dist-packages extra-addons
cd /odoo/ar/odoo-17.0/
sudo rm -rf dist-local-packages dist-packages extra-addons
cd /odoo/ar/odoo-18.0/
sudo rm -rf dist-local-packages dist-packages extra-addons

CD="/mnt/old/home/jobiols/git-repos/docker-odoo-jeo/jeo"

set -e

versions=( 16.0 17.0 18.0 19.0)

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
