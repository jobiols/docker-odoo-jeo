FROM jobiols/odoo-jeo:19.0
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

# scripts to extract sources to host
COPY ./extract_site-packages.sh /
COPY ./extract_src.sh /

# install wdb
RUN git clone https://@github.com/jobiols/wdb.git /opt/wdb \
    && pip install --no-cache-dir  /opt/wdb/client \
    && rm -rf /opt/wdb

USER odoo
