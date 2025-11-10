FROM jobiols/odoo-jeo:16.0
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

# scripts to extract sources to host
COPY ./extract_dist-packages.sh /
COPY ./extract_dist-local-packages.sh /

# install wdb
RUN git clone https://github.com/jobiols/wdb.git /opt/wdb \
    && pip install --no-cache-dir --break-system-packages /opt/wdb/client \
    && rm -rf /opt/wdb

# Para debugear con visual studio sin esto no anda el debugger wdb 
RUN pip3 install debugpy

# Hacer el parche para que no cheque password
RUN sed -i  "s/raise AccessDenied()/pass/" /usr/lib/python3/dist-packages/odoo/addons/base/models/res_users.py

RUN apt install procps -y

USER odoo
