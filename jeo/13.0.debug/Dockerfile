FROM jobiols/odoo-jeo:13.0
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

# scripts to extract sources to host
COPY ./extract_dist-packages.sh /
COPY ./extract_dist-local-packages.sh /

# install wdb
RUN pip3 install wdb

# Hacer el parche para que no cheque password
RUN sed -i  "s/if not valid:/if valid:/" /usr/lib/python3/dist-packages/odoo/addons/base/models/res_users.py

# requerimiento para odoo-uml
#RUN apt-get install default-jdk -y

USER odoo
