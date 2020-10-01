FROM jobiols/odoo-jeo:13.0
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

# scripts to extract sources to host
COPY ./extract_dist-packages.sh /
COPY ./extract_dist-local-packages.sh /

# install wdb
RUN pip3 install wdb

# requerimiento para odoo-uml
RUN apt-get install default-jdk -y

USER odoo
