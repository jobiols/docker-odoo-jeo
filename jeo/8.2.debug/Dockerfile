FROM jobiols/odoo-jeo:8.2
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root
# scripts to extract sources to host
COPY ./extract_dist-packages.sh /
COPY ./extract_dist-local-packages.sh /
COPY ./extract_extra-addons.sh /

# install wdb
RUN pip install wdb

# Hacer el parche para que no cheque password
RUN sed -i  "s/[('id','=',uid),('password','=',password)]/[('id','=',uid)]/" /usr/lib/python2.7/dist-packages/openerp/addons/base/res/res_users.py

USER odoo
