FROM jobiols/odoo-jeo:19.0
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

# scripts to extract sources to host
COPY ./extract_site-packages.sh /
COPY ./extract_src.sh /

# install wdb
RUN /odoo/venv/bin/pip install --no-cache-dir \
    https://github.com/jobiols/wdb/archive/refs/heads/master.tar.gz#subdirectory=client

# sin esto no anda el wdb
RUN pip install --break-system-packages debugpy


USER odoo
