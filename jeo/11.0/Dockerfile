FROM debian:stretch-slim AS base-image
LABEL Odoo S.A. <info@odoo.com>

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8

# Use backports to avoid install some libs with pip
RUN echo 'deb http://deb.debian.org/debian stretch-backports main' > /etc/apt/sources.list.d/backports.list

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
RUN apt-get update \
        && apt-get install -y --no-install-recommends \
            ca-certificates \
            curl \
            dirmngr \
            fonts-noto-cjk \
            gnupg \
            libssl1.0-dev \
            node-less \
            python3-num2words \
            python3-pip \
            python3-phonenumbers \
            python3-pyldap \
            python3-qrcode \
            python3-renderpm \
            python3-setuptools \
            python3-slugify \
            python3-vobject \
            python3-watchdog \
            python3-xlrd \
            python3-xlwt \
            xz-utils \
        && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.stretch_amd64.deb \
        && echo '7e35a63f9db14f93ec7feeb0fce76b30c08f2057 wkhtmltox.deb' | sha1sum -c - \
        && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
        && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# install latest postgresql-client
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
        && GNUPGHOME="$(mktemp -d)" \
        && export GNUPGHOME \
        && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \
        && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \
        && gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \
        && gpgconf --kill all \
        && rm -rf "$GNUPGHOME" \
        && apt-get update  \
        && apt-get install --no-install-recommends -y postgresql-client \
        && rm -f /etc/apt/sources.list.d/pgdg.list \
        && rm -rf /var/lib/apt/lists/*

# Install Odoo
ENV ODOO_VERSION 11.0
ENV ODOO_RELEASE=latest
#ARG ODOO_SHA=e21c34a263785eea09babd7a0d876ba05c841935
RUN curl -o odoo.deb -sSL http://nightly.odoo.com/${ODOO_VERSION}/nightly/deb/odoo_${ODOO_VERSION}.${ODOO_RELEASE}_all.deb \
        && apt-get update \
        && apt-get -y install --no-install-recommends ./odoo.deb\
        && rm -rf /var/lib/apt/lists/* odoo.deb

# Copy entrypoint script and Odoo configuration file
COPY ./entrypoint.sh /
COPY ./odoo.conf /etc/odoo/

# Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
RUN chown odoo /etc/odoo/odoo.conf \
    && mkdir -p /mnt/extra-addons \
    && chown -R odoo /mnt/extra-addons
VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]

# Expose Odoo services
EXPOSE 8069 8072

# Set the default config file
ENV ODOO_RC /etc/odoo/odoo.conf

COPY wait-for-psql.py /usr/local/bin/wait-for-psql.py

# Set default user when running the container
USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]

###############################################################################
############################ Fin de base image ################################
###############################################################################

FROM base-image
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

# instalar ultima version de pip
RUN curl -fsSL https://bootstrap.pypa.io/pip/3.5/get-pip.py -o get-pip.py
RUN python3 get-pip.py
RUN pip install install --ignore-installed psycopg2-binary

# Other requirements, useful tools and recommendations to run Odoo (libldap2-dev
# libsasl2-dev re recommended by odoo here https://www.odoo.com/documentation/11.0/setup/install.html).
# libcups2-dev is for aeroo. Then install locales and later clean everything
RUN apt-get -qq update && apt-get install -yqq --no-install-recommends \
    git ssh wget unzip iputils-ping \
    libldap2-dev \
    libsasl2-dev \
    locales \
    && rm -rf /var/lib/apt/lists/* \
    && locale-gen en_US.UTF-8 && update-locale \
    && locale-gen es_AR.UTF-8 && update-locale \
    && echo 'LANG="en_US.UTF-8"' > /etc/default/locale

RUN pip3 install wheel vobject qrcode git+https://github.com/OCA/openupgradelib/@master \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN apt-get -qq update && apt-get install -yqq --no-install-recommends \
    build-essential \
    python3-dev \
    python-dev \
    libssl-dev swig \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements /req
RUN     pip3 install -r /req/adhoc-account-payment.txt \
    &&  pip3 install -r /req/l10n_ar_fe_qr.txt \
    &&  pip3 install -r /req/adhoc-aeroo_reports.txt \
    &&  pip3 install -r /req/adhoc-argentina-reporting.txt \
    &&  pip3 install -r /req/adhoc-odoo-argentina.txt \
    &&  pip3 install -r /req/adhoc-argentina-sale.txt \
    &&  pip3 install -r /req/adhoc-miscellaneous.txt \
    &&  pip3 install -r /req/adhoc-odoo-support.txt \
    &&  pip3 install -r /req/adhoc-product.txt \
    &&  pip3 install -r /req/oca-server-tools.txt \
    &&  pip3 install -r /req/oca-web.txt \
    &&  pip3 install -r /req/oca-rest-framework.txt \
#    &&  pip3 install -r /req/oca-connector.txt \
    &&  pip3 install -r /req/oca-partner-contact.txt \
    &&  pip3 install -r /req/oca-geospatial.txt \
    &&  pip3 install -r /req/fecr.txt \
    &&  pip3 install -r /req/oca-openupgradelib.txt \
    &&  pip3 install -r /req/requirements.txt \
    && rm -r /req

# crear cache para pyafipws lo necesita para actualizar desde padron y darle
# permisos para que pueda escribir desde pyafipws porque ahi hay una base
# sqlite que se usa cuando se refrescan actividades, impuestos y conceptos.
RUN mkdir /usr/local/lib/python3.5/dist-packages/pyafipws/cache
RUN chmod -R o+w /usr/local/lib/python3.5/dist-packages/pyafipws

# Make auto_install = False for various modules
RUN sed  -i  "s/'auto_install': True/'auto_install': False/" /usr/lib/python3/dist-packages/odoo/addons/l10n_ar/__manifest__.py

# bajar el cifrado del cliente para evitar el error DH_KEY_TOO_SMALL
# parece que la afip tiene un cifrado debil.
RUN sed -i  "s/CipherString = DEFAULT@SECLEVEL=2/CipherString = DEFAULT@SECLEVEL=1/" /etc/ssl/openssl.cnf

# create directory for odoo files
ENV ETC_DIR /opt/odoo/etc
ENV DATA_DIR /opt/odoo/data
ENV CUSTOM_ADDONS /opt/odoo/custom-addons
ENV EXTRA_ADDONS /opt/odoo/extra-addons
RUN    mkdir -p /opt/odoo \
    && mkdir -p ${ETC_DIR} \
    && mkdir -p ${DATA_DIR} \
    && mkdir -p ${CUSTOM_ADDONS} \
    && mkdir -p ${EXTRA_ADDONS} \
    && chown -R odoo.odoo /opt/odoo

# Reset the default config file
ENV ODOO_RC /opt/odoo/etc/odoo.conf

COPY ./resources/ /opt/odoo/resources/

# Fix point_of_sale
COPY ./resources/devices.js /usr/lib/python3/dist-packages/odoo/addons/point_of_sale/static/src/js/

USER odoo
