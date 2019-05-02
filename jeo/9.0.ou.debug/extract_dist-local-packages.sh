#!/bin/bash
################################################################
# Extrae los odoo packages de la imagen al host para desarrollo

cp -r /usr/local/lib/python2.7/dist-packages/* /mnt/dist-local-packages/
