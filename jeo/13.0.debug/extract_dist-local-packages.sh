#!/bin/bash
################################################################
# Extrae los odoo packages de la imagen al host para desarrollo
# revision 2020-02-24

rm -r /mnt/dist-local-packages/*
cp -r /usr/local/lib/python3.7/dist-packages/* /mnt/dist-local-packages/
