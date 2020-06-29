FROM jobiols/odoo-jeo:9.1
MAINTAINER Jorge Obiols <jorge.obiols@gmail.com>

USER root

# scripts to extract sources to host
COPY ./extract_dist-packages.sh /
COPY ./extract_dist-local-packages.sh /
COPY ./extract_extra-addons.sh /

# requerimiento para odoo-uml
RUN apt-get update && apt-get install default-jdk -y

# install wdb
RUN pip install wdb

USER odoo