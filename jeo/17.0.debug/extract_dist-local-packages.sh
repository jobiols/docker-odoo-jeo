#!/bin/bash
################################################################
# Extrae los odoo packages de la imagen al host para desarrollo
# revision 2021-10-08

rm -r /mnt/dist-local-packages/*
cp -r /usr/local/lib/python3.9/dist-packages/* /mnt/dist-local-packages/
