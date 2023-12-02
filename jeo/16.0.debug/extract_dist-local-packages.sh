#!/bin/bash
################################################################
# Extrae los odoo packages de la imagen al host para desarrollo
# revision 2023-11-02

cp -r /usr/local/lib/python3.9/dist-packages/* /mnt/dist-local-packages/
