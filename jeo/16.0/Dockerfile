# 0.749
# con fuentes 1.82

#######################################
# Etapa 1: compilar Python 3.10.12
#######################################
FROM debian:bullseye-slim AS builder
ARG PYTHON_VERSION=3.10.12
ENV DEBIAN_FRONTEND=noninteractive

# Dependencias de compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates \
    libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
    libsqlite3-dev libffi-dev libncursesw5-dev xz-utils tk-dev

# Descargar y compilar
WORKDIR /tmp
RUN curl -SL https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz \
    | tar -xz \
 && cd Python-${PYTHON_VERSION} \
 && ./configure --prefix=/opt/python --enable-optimizations --with-ensurepip=install \
 && make -j"$(nproc)" \
 && make altinstall

# Podar cachés y tests para achicar tamaño
RUN find /opt/python -name '__pycache__' -type d -exec rm -rf {} + \
 && rm -rf /opt/python/lib/python*/test

# Limpiar build‑deps
RUN apt-get purge -y --auto-remove build-essential curl \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/*

#######################################
# Etapa 2: runtime mínimo
#######################################
FROM debian:bullseye-slim
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

ARG PYTHON_VERSION=3.10.12
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/opt/python/bin:${PATH}"
# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG=C.UTF-8

# Solo librerías necesarias en runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl1.1 libffi7 libbz2-1.0 libreadline8 \
    libsqlite3-0 libncursesw6 zlib1g xz-utils tk \
 && rm -rf /var/lib/apt/lists/*

# Copiar Python construido desde la etapa de compilación
COPY --from=builder /opt/python /opt/python

# Symlinks útiles
RUN ln -s /opt/python/bin/python3.10 /usr/local/bin/python3 \
 && ln -s /opt/python/bin/pip3.10     /usr/local/bin/pip

ARG TARGETARCH
SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Instalar wkhtmltopdf según la arquitectura
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git && \
    if [ -z "${TARGETARCH}" ]; then \
        TARGETARCH="$(dpkg --print-architecture)"; \
    fi; \
    WKHTMLTOPDF_ARCH=${TARGETARCH} && \
    case ${TARGETARCH} in \
    "amd64") WKHTMLTOPDF_ARCH=amd64 && WKHTMLTOPDF_SHA=9df8dd7b1e99782f1cfa19aca665969bbd9cc159  ;; \
    "arm64")  WKHTMLTOPDF_SHA=58c84db46b11ba0e14abb77a32324b1c257f1f22  ;; \
    "ppc64le" | "ppc64el") WKHTMLTOPDF_ARCH=ppc64el && WKHTMLTOPDF_SHA=7ed8f6dcedf5345a3dd4eeb58dc89704d862f9cd  ;; \
    esac \
    && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bullseye_${WKHTMLTOPDF_ARCH}.deb \
    && echo ${WKHTMLTOPDF_SHA} wkhtmltox.deb | sha1sum -c - \
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# Instalar cliente de PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends gnupg ca-certificates \
 && echo 'deb http://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
 && export GNUPGHOME="$(mktemp -d)" \
 && gpg --batch --keyserver hkps://keyserver.ubuntu.com --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8 \
 && gpg --batch --armor --export B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8 > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \
 && gpgconf --kill all \
 && rm -rf "$GNUPGHOME" \
 && apt-get update \
 && apt-get install -y --no-install-recommends postgresql-client \
 && rm -f /etc/apt/sources.list.d/pgdg.list \
 && rm -rf /var/lib/apt/lists/*

# Install rtlcss (soporte RTL, escribir lenguajes de derecha a izq como árabe o hebreo) hacer esto en la primera etapa
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        npm && \
    # Instalar rtlcss
    npm install -g rtlcss

# instalar fuentes de odoo community para chino y japonés
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        fonts-noto-cjk

# Instalar odoo community
ENV ODOO_VERSION=16.0
ARG ODOO_RELEASE=${ODOO_RELEASE}

RUN git clone --depth 1 --branch ${ODOO_VERSION} \
    https://github.com/odoo/odoo.git /usr/lib/python3/dist-packages/odoo

# Cambiar uid y gid en odoo para que coincidan con el usuario del host
RUN groupadd -g 1100 odoo && \
    useradd -u 1100 -g odoo -m -s /bin/bash odoo

# Copy entrypoint script and Odoo configuration file, and wait-for-psql script
COPY ./entrypoint.sh /
COPY ./odoo.conf /etc/odoo/
COPY ./wait-for-psql.py /usr/local/bin/wait-for-psql.py

# Set permissions and Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
RUN chown odoo /etc/odoo/odoo.conf \
    && mkdir -p /mnt/extra-addons \
    && chown -R odoo /mnt/extra-addons
VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]

# Expose Odoo services
EXPOSE 8069 8071 8072

# Set the default config file
ENV ODOO_RC=/etc/odoo/odoo.conf

ENV ETC_DIR=/opt/odoo/etc
ENV DATA_DIR=/opt/odoo/data
ENV LOG_DIR=/var/log/odoo
ENV BKP_DIR=/var/odoo/backups
ENV ADDONS_DIR=/opt/odoo/custom-addons
ENV ODOO_RC=${ETC_DIR}/odoo.conf
RUN \
       mkdir -p ${ETC_DIR} \
    && mkdir -p ${DATA_DIR} \
    && mkdir -p ${LOG_DIR} \
    && mkdir -p ${BKP_DIR} \
    && mkdir -p ${ADDONS_DIR} \
    && chown -R odoo.odoo /opt/odoo \
    && chown -R odoo.odoo /var/odoo

# Instala las dependencias del sistema operativo, incluyendo las de desarrollo de PostgreSQL.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    libldap2-dev \
    libsasl2-dev \
    libffi-dev \
    libssl-dev \
    libev-dev \
    pkg-config \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala las dependencias de Python.
# Este bloque ya está correcto y no necesita cambios.
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir "cython<3.0" && \
    pip install \
        --no-cache-dir \
        --no-build-isolation \
        -r /usr/lib/python3/dist-packages/odoo/requirements.txt


# Set default user when running the container
# USER odoo

# ENTRYPOINT ["/entrypoint.sh"]
# CMD ["odoo"]





# # Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#         ca-certificates \
#         curl \
#         dirmngr \
#         fonts-noto-cjk \
#         gnupg \
#         libssl-dev \
#         node-less \
#         npm \
#         python3-magic \
#         python3-num2words \
#         python3-odf \
#         python3-pdfminer \
#         python3-pip \
#         python3-phonenumbers \
#         python3-pyldap \
#         python3-qrcode \
#         python3-renderpm \
#         python3-setuptools \
#         python3-slugify \
#         python3-vobject \
#         python3-watchdog \
#         python3-xlrd \
#         python3-xlwt \
#         xz-utils && \
#     if [ -z "${TARGETARCH}" ]; then \
#         TARGETARCH="$(dpkg --print-architecture)"; \
#     fi; \
#     WKHTMLTOPDF_ARCH=${TARGETARCH} && \
#     case ${TARGETARCH} in \
#     "amd64") WKHTMLTOPDF_ARCH=amd64 && WKHTMLTOPDF_SHA=9df8dd7b1e99782f1cfa19aca665969bbd9cc159  ;; \
#     "arm64")  WKHTMLTOPDF_SHA=58c84db46b11ba0e14abb77a32324b1c257f1f22  ;; \
#     "ppc64le" | "ppc64el") WKHTMLTOPDF_ARCH=ppc64el && WKHTMLTOPDF_SHA=7ed8f6dcedf5345a3dd4eeb58dc89704d862f9cd  ;; \
#     esac \
#     && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bullseye_${WKHTMLTOPDF_ARCH}.deb \
#     && echo ${WKHTMLTOPDF_SHA} wkhtmltox.deb | sha1sum -c - \
#     && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
#     && rm -rf /var/lib/apt/lists/* wkhtmltox.deb


# # Install rtlcss (on Debian buster)
# RUN npm install -g rtlcss

# # Install Odoo
# ENV ODOO_VERSION=16.0
# ARG ODOO_RELEASE=20250613
# #ARG ODOO_SHA=1fb02a432e076dd71aca7a7611a07223919356b9
# RUN curl -o odoo.deb -sSL http://nightly.odoo.com/${ODOO_VERSION}/nightly/deb/odoo_${ODOO_VERSION}.${ODOO_RELEASE}_all.deb \
# #    && echo "${ODOO_SHA} odoo.deb" | sha1sum -c - \
#     && apt-get update \
#     && apt-get -y install --no-install-recommends ./odoo.deb \
#     && rm -rf /var/lib/apt/lists/* odoo.deb

# #Cambiar uid y gid en odoo
# RUN groupmod -g 1100 odoo \
#   && usermod -u 1100 -g 1100 odoo

# # Copy entrypoint script and Odoo configuration file
# COPY ./entrypoint.sh /
# COPY ./odoo.conf /etc/odoo/

# # Set permissions and Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
# RUN chown odoo /etc/odoo/odoo.conf \
#     && mkdir -p /mnt/extra-addons \
#     && chown -R odoo /mnt/extra-addons
# VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]

# # Expose Odoo services
# EXPOSE 8069 8071 8072

# # Set the default config file
# ENV ODOO_RC=/etc/odoo/odoo.conf

# COPY wait-for-psql.py /usr/local/bin/wait-for-psql.py

# # Set default user when running the container
# USER odoo

# ENTRYPOINT ["/entrypoint.sh"]
# CMD ["odoo"]

# ###############################################################################
# ############################ Fin de base image ################################
# ###############################################################################

# FROM base-image
# LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

# USER root

# ENV ETC_DIR=/opt/odoo/etc
# ENV DATA_DIR=/opt/odoo/data
# ENV LOG_DIR=/var/log/odoo
# ENV BKP_DIR=/var/odoo/backups
# ENV ADDONS_DIR=/opt/odoo/custom-addons
# ENV ODOO_RC=${ETC_DIR}/odoo.conf
# RUN \
#        mkdir -p ${ETC_DIR} \
#     && mkdir -p ${DATA_DIR} \
#     && mkdir -p ${LOG_DIR} \
#     && mkdir -p ${BKP_DIR} \
#     && mkdir -p ${ADDONS_DIR} \
#     && chown -R odoo.odoo /opt/odoo \
#     && chown -R odoo.odoo /var/odoo

# # instalar el ultimo pip
# RUN curl -fsSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
#     && python3 get-pip.py \
#     && rm get-pip.py

# RUN apt-get -qq update && apt-get install -yqq --no-install-recommends \
#     git python3-dev build-essential

# COPY ./requirements /req
# RUN pip3 install -r /req/requirements.txt
# RUN pip3 install -r /req/odoo-argentina.txt
# #RUN pip3 install -r /req/adhoc-aeroo_reports.txt
# RUN rm -r /req

# # crear cache para pyafipws lo necesita para actualizar desde padron y darle
# # permisos para que pueda escribir desde pyafipws porque ahi hay una base
# # sqlite que se usa cuando se refrescan actividades, impuestos y conceptos.
# RUN mkdir /usr/local/lib/python3.9/dist-packages/pyafipws/cache
# RUN chmod -R 777 /usr/local/lib/python3.9/dist-packages/pyafipws

# # bajar el cifrado del cliente para evitar el error DH_KEY_TOO_SMALL
# # parece que la afip tiene un cifrado debil.
# RUN sed -i  "s/CipherString = DEFAULT@SECLEVEL=2/CipherString = DEFAULT@SECLEVEL=1/" /etc/ssl/openssl.cnf

# USER odoo
