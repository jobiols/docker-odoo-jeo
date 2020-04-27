#!/usr/bin/env bash
################################################################
# Extrae los odoo extra addons de la imagen al host para desarrollo

rm -r /mnt/extra-addons/*
cp -r /opt/odoo/extra-addons/* /mnt/extra-addons/

