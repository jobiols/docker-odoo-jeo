FROM ubuntu:noble
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG=en_US.UTF-8
ENV ODOO_VERSION=19.0
ENV ODOO_HOME=/usr/lib/python3/dist-packages/odoo
ARG ODOO_RELEASE
ENV ODOO_RELEASE=${ODOO_RELEASE}

# Retrieve the target architecture to install the correct wkhtmltopdf package
ARG TARGETARCH

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        dirmngr \
        fonts-noto-cjk \
        gnupg \
        libssl-dev \
        node-less \
        npm \
#        python3-magic \
#        python3-num2words \
#        python3-odf \
#        python3-pdfminer \
        python3-pip \
#        python3-phonenumbers \
#        python3-pyldap \
#        python3-qrcode \
#        python3-renderpm \
#        python3-setuptools \
#        python3-slugify \
#        python3-vobject \
#        python3-watchdog \
#        python3-xlrd \
#        python3-xlwt \
        python3-venv \
        xz-utils && \
    if [ -z "${TARGETARCH}" ]; then \
        TARGETARCH="$(dpkg --print-architecture)"; \
    fi; \
    WKHTMLTOPDF_ARCH=${TARGETARCH} && \
    case ${TARGETARCH} in \
    "amd64") WKHTMLTOPDF_ARCH=amd64 && WKHTMLTOPDF_SHA=967390a759707337b46d1c02452e2bb6b2dc6d59  ;; \
    "arm64")  WKHTMLTOPDF_SHA=90f6e69896d51ef77339d3f3a20f8582bdf496cc  ;; \
    "ppc64le" | "ppc64el") WKHTMLTOPDF_ARCH=ppc64el && WKHTMLTOPDF_SHA=5312d7d34a25b321282929df82e3574319aed25c  ;; \
    esac \
    && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.jammy_${WKHTMLTOPDF_ARCH}.deb \
    && echo ${WKHTMLTOPDF_SHA} wkhtmltox.deb | sha1sum -c - \
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# Instalar un entorno virtual para evitar conflictos con versiones de pip y setuptools
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# install latest postgresql-client
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ noble-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
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

# # Agregar los headers para que psycopg2 pueda compilar
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ noble-pgdg main' > /etc/apt/sources.list.d/pgdg.list
RUN apt-get update && apt-get install -y libpq-dev

# # Agregar biblotecas requeridas para compilar python-ldap
RUN apt-get install -y libldap2-dev libsasl2-dev

# Create ODOO system user The user should NOT be added to the sudo'ers group.
RUN adduser --system --quiet --shell=/bin/bash --home=/odoo --gecos 'ODOO' --group odoo

# Install Odoo latest version
RUN git clone --depth 1 --branch ${ODOO_VERSION} https://www.github.com/odoo/odoo ${ODOO_HOME}
ENV PATH="$PATH:/usr/lib/python3/dist-packages/odoo"

RUN apt-get -qq update && apt-get install -yqq --no-install-recommends \
    python3-dev build-essential gcc

# Install Odoo requirements
RUN pip install -r /usr/lib/python3/dist-packages/odoo/requirements.txt

# Set permissions and Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
# RUN mkdir -p /mnt/extra-addons \
#     && chown -R odoo /mnt/extra-addons
# VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]

# Expose Odoo services
EXPOSE 8069 8071 8072

ENV ETC_DIR=/opt/odoo/etc
ENV DATA_DIR=/opt/odoo/data
ENV LOG_DIR=/var/log/odoo
ENV BKP_DIR=/var/odoo/backups
ENV ADDONS_DIR=/opt/odoo/custom-addons
ENV ODOO_RC=${ETC_DIR}/odoo.conf
RUN \
       mkdir -p ${ETC_DIR} \
    && mkdir -p ${DATA_DIR} \
    && mkdir -p ${ADDONS_DIR} \
    && mkdir -p ${BKP_DIR} \
    && chown -R odoo.odoo /opt/odoo \
    && chown -R odoo.odoo /var/odoo

# Copy entrypoint script and Odoo configuration file
COPY entrypoint.sh /
COPY odoo.conf $ETC_DIR/
COPY wait-for-psql.py /usr/local/bin/wait-for-psql.py

# Instalar todas las dependencias de los modulos a instalar
COPY ./requirements /req
#RUN pip3 install -r /req/odoo-core-requirements.txt
#RUN pip3 install -r /req/odoo-argentina.txt
#RUN pip3 install -r /req/adhoc-aeroo_reports.txt
RUN pip3 install -r /req/requirements.txt
RUN rm -r /req

USER odoo
ENTRYPOINT ["/entrypoint.sh"]
