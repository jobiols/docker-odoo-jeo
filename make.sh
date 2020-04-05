#!/usr/bin/env bash
#
# Script par hacer Build de las imagenes solo local
# Para hacer el build en docker pushear este repo en github

cd jeo/11.0
if ! ./make.sh;
then
    echo "Failed odoo-jeo:11.0"
	exit 1
else
    echo "----------> Success odoo-jeo:11.0"
fi

cd ../11.0.debug
if ! ./make.sh;
then
    echo "Failed jeo-11.0.debug"
	exit 1
else
    echo "----------> Success odoo-jeo:11.0.debug"
fi

cd ../12.0
if ! ./make.sh;
then
    echo "Failed odoo-jeo:12.0"
	exit 1
else
    echo "----------> Success odoo-jeo:12.0"
fi

cd ../12.0.debug
if ! ./make.sh;
then
    echo "Failed odoo-jeo:12.0.debug"
	exit 1
else
    echo "----------> Success odoo-jeo:12.0.debug"
fi

cd ../13.0
if ! ./make.sh;
then
    echo "Failed odoo-jeo:13.0"
	exit 1
else
    echo "----------> Success odoo-jeo:13.0"
fi

cd ../13.0.debug
if ! ./make.sh;
then
    echo "Failed odoo-jeo:13.0.debug"
	exit 1
else
    echo "----------> Success odoo-jeo:13.0.debug"
fi

cd ../14.0
if ! ./make.sh;
then
    echo "Failed odoo-jeo:14.0"
	exit 1
else
    echo "----------> Success odoo-jeo:14.0"
fi

cd ../14.0.debug
if ! ./make.sh;
then
    echo "Failed odoo-jeo:14.0.debug"
	exit 1
else
    echo "----------> Success odoo-jeo:14.0.debug"
fi


