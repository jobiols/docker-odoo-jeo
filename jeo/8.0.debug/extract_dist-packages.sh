#!/bin/bash
################################################################
# Extrae los odoo packages de la imagen al host para desarrollo

rm -r /mnt/dist-packages/*
cp -r /usr/lib/python2/dist-packages/* /mnt/dist-packages/
