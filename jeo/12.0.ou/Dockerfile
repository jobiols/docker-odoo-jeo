FROM jobiols/odoo-jeo:12.0
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

# borrar odoo
RUN rm -r /usr/lib/python3/dist-packages/odoo/*

# Bajar openupgrade en directorio temporario
RUN git clone -b 12.0 --depth 1 https://github.com/oca/OpenUpgrade.git /opt/openupgrade

# copiar los fuentes
RUN cp -r /opt/openupgrade/odoo/* /usr/lib/python3/dist-packages/odoo
RUN cp -r /opt/openupgrade/addons/* /usr/lib/python3/dist-packages/odoo/addons

# no queremos instalar esto porue ya esta y da un error al actualizar
RUN sed -i '/XlsxWriter/d' /opt/openupgrade/requirements.txt
RUN sed -i '/pyserial/d' /opt/openupgrade/requirements.txt
RUN sed -i '/pyldap/d' /opt/openupgrade/requirements.txt
#RUN sed -i '/psycopg2/d' /opt/openupgrade/requirements.txt
RUN sed -i '/psutil/d' /opt/openupgrade/requirements.txt
RUN sed -i '/greenlet/d' /opt/openupgrade/requirements.txt
RUN sed -i '/docutils/d' /opt/openupgrade/requirements.txt

RUN pip3 install -r /opt/openupgrade/requirements.txt --ignore-installed

USER odoo
