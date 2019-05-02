#!/usr/bin/env bash
cd odoo/11.0
if ! ./make.sh;
then
    echo "Failed odoo-11.0"
	exit 1
fi

cd ../../jeo/11.0

if ! ./make.sh;
then
    echo "Failed jeo-11.0"
	exit 1
fi

cd ../../jeo/11.0.debug

if ! ./make.sh;
then
    echo "Failed jeo-11.0.debug"
	exit 1
fi

cd ../../odoo/12.0

if ! ./make.sh;
then
    echo "Failed odoo-12.0"
	exit 1
fi

cd ../../jeo/12.0

if ! ./make.sh;
then
    echo "Failed jeo-12.0"
	exit 1
fi

cd ../../jeo/12.0.debug

if ! ./make.sh;
then
    echo "Failed jeo-12.0.debug"
	exit 1
fi
