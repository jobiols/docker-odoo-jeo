#!/bin/bash
################################################################
# Extrae los odoo packages de la imagen al host para desarrollo
# revision 2023-11-17

rm -rf /mnt/dist-packages/*
cp -rp /usr/lib/python3/dist-packages/* /mnt/dist-packages/
