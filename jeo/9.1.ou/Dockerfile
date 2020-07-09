FROM jobiols/odoo-jeo:9.1
LABEL Jorge Obiols <jorge.obiols@gmail.com>

USER root

# borrar odoo
RUN rm -r /usr/lib/python2.7/dist-packages/openerp/*

# Bajar openupgrade en directorio temporario
RUN git clone -b 9.0 --depth 1 https://github.com/jobiols/OpenUpgrade.git /opt/openupgrade

# copiar los fuentes
RUN cp -r /opt/openupgrade/openerp/* /usr/lib/python2.7/dist-packages/openerp
RUN cp -r /opt/openupgrade/addons/* /usr/lib/python2.7/dist-packages/openerp/addons

# scripts to extract sources to host
COPY ./extract_dist-packages.sh /
COPY ./extract_dist-local-packages.sh /
COPY ./extract_extra-addons.sh /

# install wdb
RUN pip install wdb

COPY ./requirements /req
RUN pip install -r /req/openupgrade-requirements.txt
RUN pip install -r /req/openupgrade-requirements1.txt

USER odoo
