FROM jobiols/odoo-jeo:8.1
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

# Actualizar pyafipws
RUN git clone -b master --depth 1 https://github.com/reingart/pyafipws.git /pyafipws
RUN rm -r /usr/local/lib/python2.7/dist-packages/pyafipws
RUN mv /pyafipws /usr/local/lib/python2.7/dist-packages

# crear cache para pyafipws lo necesita para actualizar desde padron y darle
# permisos para que pueda escribir desde pyafipws porque ahi hay una base
# sqlite que se usa cuando se refrescan actividades, impuestos y conceptos.
RUN mkdir /usr/local/lib/python2.7/dist-packages/pyafipws/cache
RUN chmod -R o+w /usr/local/lib/python2.7/dist-packages/pyafipws

USER odoo
