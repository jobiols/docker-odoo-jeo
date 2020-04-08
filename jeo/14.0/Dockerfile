FROM debian:buster-slim AS base-image
MAINTAINER Odoo S.A. <info@odoo.com>

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
RUN set -x; \
        apt-get update \
        && apt-get install -y --no-install-recommends \
            ca-certificates \
            curl \
            dirmngr \
            fonts-noto-cjk \
            gnupg \
            libssl-dev \
            node-less \
            npm \
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
RUN set -x; \
        echo 'deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
        && export GNUPGHOME="$(mktemp -d)" \
        && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \
        && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \
        && gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \
        && gpgconf --kill all \
        && rm -rf "$GNUPGHOME" \
        && apt-get update  \
        && apt-get install -y postgresql-client \
        && rm -rf /var/lib/apt/lists/*

# Install rtlcss (on Debian buster)
RUN set -x; \
    npm install -g rtlcss

# Install Odoo
ENV ODOO_VERSION master
ARG ODOO_RELEASE=latest

RUN set -x; \
        curl -o odoo.deb -sSL http://nightly.odoo.com/${ODOO_VERSION}/nightly/deb/odoo_14.0alpha1.latest_all.deb \
        && dpkg --force-depends -i odoo.deb \
        && apt-get update \
        && apt-get -y install -f --no-install-recommends \
        && rm -rf /var/lib/apt/lists/* odoo.deb

# Copy entrypoint script and Odoo configuration file
COPY ./entrypoint.sh /
COPY ./odoo.conf /etc/odoo/

# Set permissions and Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
RUN chown odoo /etc/odoo/odoo.conf \
    && mkdir -p /mnt/extra-addons \
    && chown -R odoo /mnt/extra-addons
VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]

# Expose Odoo services
EXPOSE 8069 8071

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
MAINTAINER Jorge Obiols <jorge.obiols@gmail.com>
ENV Release 2020-04-05

USER root

ENV ETC_DIR /opt/odoo/etc
ENV DATA_DIR /opt/odoo/data
ENV LOG_DIR /var/log/odoo
ENV BKP_DIR /var/odoo/backups
ENV ADDONS_DIR /opt/odoo/custom-addons
ENV ODOO_RC ${ETC_DIR}/odoo.conf
RUN \
       mkdir -p ${ETC_DIR} \
    && mkdir -p ${DATA_DIR} \
    && mkdir -p ${LOG_DIR} \
    && mkdir -p ${BKP_DIR} \
    && mkdir -p ${ADDONS_DIR} \
    && chown -R odoo.odoo /opt/odoo \
    && chown -R odoo.odoo /var/odoo

# Other requirements, useful tools and recommendations to run Odoo (libldap2-dev
# libsasl2-dev re recommended by odoo here https://www.odoo.com/documentation/11.0/setup/install.html).
# libcups2-dev is for aeroo. Then install locales and later clean everything
RUN apt-get -qq update && apt-get install -yqq --no-install-recommends \
    git \
    python3-dev build-essential

#    ssh wget unzip iputils-ping \
#    libldap2-dev libsasl2-dev \
#    libcups2-dev \
#    locales \
#    && locale-gen en_US.UTF-8 && update-locale \
#    && locale-gen es_AR.UTF-8 && update-locale \
#    && echo 'LANG="en_US.UTF-8"' > /etc/default/locale \
#    && pip3 install --no-cache-dir --upgrade pip setuptools

#RUN pip3 install git+https://github.com/OCA/openupgradelib/@master
# num2words wheel vobject qrcode
#    && apt-get purge -yqq build-essential '*-dev' \
#    && apt-get -yqq autoremove \
#    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# requisites for M2Crypto
#RUN apt-get update -qq
#RUN apt-get install build-essential python3-dev python-dev libssl-dev swig -y -qq

#COPY ./requirements /req
#RUN pip3 install -r /req/requirements.txt
#RUN pip3 install -r /req/adhoc-account-payment.txt
#RUN pip3 install -r /req/adhoc-aeroo_reports.txt
#RUN pip3 install -r /req/adhoc-argentina-reporting.txt
#RUN pip3 install -r /req/adhoc-argentina-sale.txt
#RUN pip3 install -r /req/adhoc-miscellaneous.txt
#RUN pip3 install -r /req/adhoc-odoo-support.txt
#RUN pip3 install -r /req/adhoc-product.txt
#RUN pip3 install -r /req/adhoc-odoo-argentina.txt
#RUN pip3 install -r /req/oca-server-tools.txt
#RUN pip3 install -r /req/oca-web.txt
#RUN pip3 install -r /req/oca-rest-framework.txt
#RUN pip3 install -r /req/oca-partner-contact.txt
#RUN pip3 install -r /req/adhoc-reporting-engine.txt # esto no anda por el pycups
#RUN rm -r /req

# crear cache para pyafipws
#RUN mkdir /usr/local/lib/python3.5/dist-packages/pyafipws/cache
#RUN chmod o+rw /usr/local/lib/python3.5/dist-packages/pyafipws/cache

# Mount persistent directories
#VOLUME ["${DATA_DIR}", "${CUSTOM_ADDONS}"]

# replace  entrypoint script and replace Odoo configuration file (new name)
#ENV RESOURCES /opt/odoo/resources/
#COPY ./resources/ ${RESOURCES}

# change entrypoint
#ENTRYPOINT ["/opt/odoo/resources/entrypoint.sh"]
#CMD ["odoo"]

# Variables used by the launch scripts
#ENV \
#    DB_TEMPLATE=template1 \
#    PGUSER=odoo \
#    PGPASSWORD=odoo \
#    PGHOST=db
#    ODOO_SERVER=odoo \
#    ODOO_CONF=/opt/odoo/etc/odoo.conf \
#    FIXDBS=False \
#    WAIT_PG=True \
#    PG_MAX_CONNECTIONS=100 \
#    # odoo conf variables
#    MAX_CRON_THREADS=1 \
#    SMTP_SERVER=localhost \
#    SMTP_PORT=25 \
#    SMTP_SSL=False \
#    SMTP_USER=False \
#    SMTP_PASSWORD=False \
#    UNACCENT=True \
#    WORKERS=6 \
#    ADMIN_PASSWORD=admin \
#    DISABLE_SESSION_GC=false \
#    PROXY_MODE=True \
#    WITHOUT_DEMO=True \
#    DBFILTER=.* \
#    LIMIT_TIME_CPU=1600 \
#    LIMIT_TIME_REAL=3200 \
#    LIMIT_MEMORY_HARD=2684354560 \
#    LIMIT_MEMORY_SOFT=2147483648 \
#    AEROO_DOCS_HOST=aeroo \
#    AFIP_HOMO_PKEY_FILE=/opt/odoo/backups/homo.pkey \
#    AFIP_HOMO_CERT_FILE=/opt/odoo/backups/homo.cert \
#    AFIP_PROD_PKEY_FILE=/opt/odoo/backups/prod.pkey \
#    AFIP_PROD_CERT_FILE=/opt/odoo/backups/prod.cert \


USER odoo