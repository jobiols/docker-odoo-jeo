FROM jobiols/odoo-jeo:11.1
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

# scripts to extract sources to host
COPY ./extract_dist-packages.sh /
COPY ./extract_dist-local-packages.sh /

RUN pip3 install \
    wdb

# Hacer el parche para que no cheque password
RUN sed -i  "s/raise AccessDenied()/pass/" /usr/lib/python3/dist-packages/odoo/addons/base/models/res_users.py

USER odoo
