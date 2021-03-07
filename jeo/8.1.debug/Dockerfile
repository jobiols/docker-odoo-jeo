FROM jobiols/odoo-jeo:8.1
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root
# scripts to extract sources to host
COPY ./extract_dist-packages.sh /
COPY ./extract_dist-local-packages.sh /
COPY ./extract_extra-addons.sh /

# install wdb
RUN pip install wdb

USER odoo
