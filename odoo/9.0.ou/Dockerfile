FROM ubuntu:xenial
MAINTAINER Juan Jose Scarafia <jjs@adhoc.com.ar>

# segun odoo esta version sigue siendo la recomendable https://github.com/odoo/odoo/wiki/Wkhtmltopdf, la 12.2.1 y las podemos encontrar acá https://wkhtmltopdf.org/downloads.html

ENV WKHTMLTOX_X64 https://downloads.wkhtmltopdf.org/0.12/0.12.5/wkhtmltox_0.12.5-1.trusty_amd64.deb

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
RUN set -x; \
        apt-get update \
        && apt-get install -y --no-install-recommends \
            ca-certificates \
            curl \
            git \
            node-less \
            node-clean-css \
            python-pyinotify \
            python-renderpm \
            python-pip \
            zlib1g
            # not anymore on ubuntu 16.04
            # python-support
RUN set -x; \
        curl -o wkhtmltox.deb -SL ${WKHTMLTOX_X64} \
        && dpkg --force-depends -i wkhtmltox.deb \
        && apt-get -y install -f --no-install-recommends \
        && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false -o APT::AutoRemove::SuggestsImportant=false npm \
        && rm -rf /var/lib/apt/lists/* wkhtmltox.deb


# Install Odoo
ENV ODOO_VERSION=9.0
ENV ODOO_RELEASE latest
RUN set -x; \
        curl -o odoo.deb -SL http://nightly.odoo.com/${ODOO_VERSION}/nightly/deb/odoo_${ODOO_VERSION}c.${ODOO_RELEASE}_all.deb \
        && dpkg --force-depends -i odoo.deb \
        && apt-get update \
        && apt-get -y install -f --no-install-recommends \
        && rm -rf /var/lib/apt/lists/* odoo.deb

# reemplazar los fuentes de odoo 9.0 por los de openupgrade 9.0
# Bajar open upgrade en directorio temporario
RUN git clone -b 9.0 --depth 1 https://github.com/OCA/OpenUpgrade.git /ou

# copiar los fuentes donde deben estar
RUN rm -r /usr/lib/python2.7/dist-packages/openerp

RUN cp -R /ou/openerp/ /usr/lib/python2.7/dist-packages/openerp
# copiamos no movemos porque en addons ya hay cosas...
RUN cp -R /ou/addons/* /usr/lib/python2.7/dist-packages/openerp/addons
# cambiamos permisos esto tarda mucho por un bug
# https://github.com/docker/for-linux/issues/388
RUN chown -R odoo:odoo /usr/lib/python2.7/dist-packages/openerp/


# actualizar requirements

# instalar pip
RUN curl -o /ou/get-pip.py https://bootstrap.pypa.io/get-pip.py
RUN python /ou/get-pip.py

RUN sed -i '/python-ldap==2.4.19/d' /ou/requirements.txt
RUN sed -i '/Pillow==3.3.2/d' /ou/requirements.txt
RUN sed -i '/gevent==1.0.2/d' /ou/requirements.txt
RUN sed -i '/gevent==1.0.2/d' /ou/requirements.txt
RUN sed -i '/greenlet==0.4.7/d' /ou/requirements.txt
RUN sed -i '/lxml==3.4.1/d' /ou/requirements.txt
RUN sed -i '/psutil==2.2.0/d' /ou/requirements.txt
RUN sed -i '/reportlab==3.1.44/d' /ou/requirements.txt
RUN sed -i '/psycopg2==2.7.3.1/d' /ou/requirements.txt
RUN pip install Pillow
RUN pip install gevent
RUN pip install psutil
RUN pip install lxml
RUN pip install -r /ou/requirements.txt
# eliminar temporario
RUN rm -r /ou

# Copy entrypoint script and Odoo configuration file
COPY ./entrypoint.sh /
#COPY ./openerp-server.conf /etc/odoo/
#RUN chown odoo /etc/odoo/openerp-server.conf

# Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
#RUN mkdir -p /mnt/extra-addons \
#        && chown -R odoo /mnt/extra-addons
#VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]
VOLUME ["/var/lib/odoo"]

# Expose Odoo services
EXPOSE 8069 8071

# Set the default config file
#ENV OPENERP_SERVER /etc/odoo/openerp-server.conf

# Set default user when running the container
USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["openerp-server"]
