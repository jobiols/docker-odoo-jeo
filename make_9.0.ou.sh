#!/usr/bin/env bash
cd odoo/9.0.ou
if ! ./make.sh;
then
    echo "Failed odoo:9.0.ou"
	exit 1
fi
echo "-------------------------- success odoo:9.0.ou"

cd ../../jeo/9.0.ou

if ! ./make.sh;
then
    echo "Failed jeo:9.0.ou"
	exit 1
fi
echo "-------------------------- success jeo:9.0.ou"

cd ../../jeo/9.0.ou.debug

if ! ./make.sh;
then
    echo "Failed jeo:9.0.ou.debug"
	exit 1
fi
echo "-------------------------- success jeo:9.0.ou.debug"

