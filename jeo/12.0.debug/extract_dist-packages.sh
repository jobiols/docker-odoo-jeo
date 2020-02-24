#!/bin/bash
################################################################
# Extrae los odoo packages de la imagen al host para desarrollo
# revision 2020-02-24

rm -r /mnt/dist-packages/*
cp -r /usr/lib/python3/dist-packages/* /mnt/dist-packages/
