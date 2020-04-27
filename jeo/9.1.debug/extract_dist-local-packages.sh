#!/bin/bash
################################################################
# Extrae los odoo packages de la imagen al host para desarrollo

# remover todos los archivos incluso los hidden
if cd /mnt/dist-local-packages/
then
rm -rf ..?* .[!.]* *
fi
# copiar los archivos de la imagen
cp -r /usr/local/lib/python2.7/dist-packages/* /mnt/dist-local-packages/
