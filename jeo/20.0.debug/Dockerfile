FROM jobiols/odoo-jeo:20.0
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

# scripts to extract sources to host
COPY ./extract_dist-packages.sh /
COPY ./extract_dist-local-packages.sh /

RUN git clone https://github.com/jobiols/wdb.git /opt/wdb \
    && pip install --no-cache-dir --break-system-packages /opt/wdb/client \
    && rm -rf /opt/wdb

USER odoo
