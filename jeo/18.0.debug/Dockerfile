FROM jobiols/odoo-jeo:18.0
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

RUN apt-get update && apt-get install -y git

# install wdb
RUN git clone https://github.com/jobiols/wdb.git /opt/wdb \
    && pip install --no-cache-dir --break-system-packages /opt/wdb/client \
    && rm -rf /opt/wdb

# sin esto no anda el wdb
RUN pip install --break-system-packages debugpy

USER odoo
