#!/bin/bash
################################################################
# Extrae los odoo packages de la imagen al host para desarrollo

cp -r /usr/lib/python3/dist-packages/* /mnt/dist-packages/
