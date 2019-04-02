FROM jobiols/odoo-jeo:11.0
MAINTAINER Jorge Obiols <jorge.obiols@gmail.com>

USER root

# scripts to extract sources to host
COPY ./extract_dist-packages.sh /
COPY ./extract_dist-local-packages.sh /
COPY ./extract_extra-addons.sh /

# install wdb
RUN pip install wdb

USER odoo