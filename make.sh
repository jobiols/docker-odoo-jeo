#!/usr/bin/env bash
cd odoo/11.0
if ! ./make.sh;
then
    echo "Failed odoo:11.0"
	exit 1
else
    echo "----------> Success odoo:11.0"
fi

cd ../12.0
if ! ./make.sh;
then
    echo "Failed odoo:12.0"
	exit 1
else
    echo "----------> Success odoo:12.0"
fi

cd ../../jeo/11.0
if ! ./make.sh;
then
    echo "Failed odoo-jeo:11.0"
	exit 1
else
    echo "----------> Success odoo-jeo:11.0"
fi

cd ../12.0
if ! ./make.sh;
then
    echo "Failed odoo-jeo:12.0"
	exit 1
else
    echo "----------> Success odoo-jeo:12.0"
fi

cd ../11.0.debug
if ! ./make.sh;
then
    echo "Failed jeo-11.0.debug"
	exit 1
else
    echo "----------> Success odoo-jeo:11.0.debug"
fi

cd ../12.0.debug
if ! ./make.sh;
then
    echo "Failed jeo-12.0.debug"
	exit 1
else
    echo "----------> Success odoo-jeo:12.0.debug"
fi
