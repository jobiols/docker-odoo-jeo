#!/bin/bash
################################################################
# Extrae los odoo packages de la imagen al host para desarrollo

cp -r /usr/local/lib/python3.5/dist-packages/* /mnt/dist-local-packages/
