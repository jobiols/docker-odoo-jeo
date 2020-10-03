FROM jobiols/odoo-jeo:11.0
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

# scripts to extract sources to host
COPY ./extract_dist-packages.sh /
COPY ./extract_dist-local-packages.sh /

# requerimiento para odoo-uml
RUN apt-get install default-jdk -y

# install wdb
RUN pip3 install wdb
# para etl
RUN pip3 install erppeek

USER odoo
