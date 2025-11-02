#!/bin/bash
################################################################
# Extrae los odoo packages de la imagen al host para desarrollo
# revision 2023-11-17

rm -rf /mnt/dist-local-packages/*
cp -r /usr/local/lib/python3.12/dist-packages/* /mnt/dist-local-packages/
