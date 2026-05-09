FROM jobiols/odoo-jeo:20.0
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

RUN apt-get update && apt-get install -y git

# install wdb
RUN git clone https://${GITHUB_TOKEN}@github.com/quilsoft-org/wdb.git /opt/wdb \
    && pip install --no-cache-dir  /opt/wdb/client \
    && rm -rf /opt/wdb

USER odoo
