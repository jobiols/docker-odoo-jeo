FROM jobiols/odoo-jeo:18.0
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

# scripts to extract sources to host
COPY ./extract_dist-packages.sh /
COPY ./extract_dist-local-packages.sh /

RUN apt-get update && apt-get install -y git

# install wdb
RUN git clone https://${GITHUB_TOKEN}@github.com/quilsoft-org/wdb.git /opt/wdb \
    && pip install --no-cache-dir --break-system-packages /opt/wdb/client \
    && rm -rf /opt/wdb

# Hacer el parche para que no cheque password
#RUN sed -i  "s/raise AccessDenied()/pass/" /usr/lib/python3/dist-packages/odoo/addons/base/models/res_users.py

USER odoo
