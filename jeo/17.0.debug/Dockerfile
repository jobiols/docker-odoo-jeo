FROM jobiols/odoo-jeo:17.0
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

# install wdb
RUN git clone https://github.com/jobiols/wdb.git /opt/wdb
RUN pip install --no-cache-dir --break-system-packages /opt/wdb/client
RUN pip install --no-cache-dir --break-system-packages /opt/wdb/server
RUN rm -rf /opt/wdb

USER odoo
