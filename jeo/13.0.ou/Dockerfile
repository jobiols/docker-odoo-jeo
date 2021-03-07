FROM jobiols/odoo-jeo:13.0
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

# borrar odoo
RUN rm -r /usr/lib/python3/dist-packages/odoo/*

# Bajar openupgrade en directorio temporario
RUN git clone -b 13.0 --depth 1 https://github.com/oca/OpenUpgrade.git /opt/openupgrade

# copiar los fuentes
RUN cp -r /opt/openupgrade/odoo/* /usr/lib/python3/dist-packages/odoo
RUN cp -r /opt/openupgrade/addons/* /usr/lib/python3/dist-packages/odoo/addons

# no queremos instalar psutil porue ya esta y da un error al actualizar
RUN sed -i '/psutil/d' /opt/openupgrade/requirements.txt

RUN pip install -r /opt/openupgrade/requirements.txt

USER odoo
