#!/bin/bash
################################################################
# Extrae los odoo packages de la imagen al host para desarrollo
# revision 2023-11-17

rm -r /mnt/dist-local-packages/*
cp -r /usr/local/lib/python3.10/dist-packages/* /mnt/dist-local-packages/
