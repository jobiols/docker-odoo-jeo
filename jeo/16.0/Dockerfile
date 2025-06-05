# ----------------------------------------------------------------------
# Etapa 1: Base con Python 3.10.12 (Bullseye)
# Peso 20250528 2.26Gb
#      20250604 2.31Gb
# ----------------------------------------------------------------------
FROM python:3.10.12-slim-bullseye AS base-image
LABEL maintainer="Odoo S.A. <info@odoo.com>"

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generar locale C.UTF-8 (requisito para Postgres y Odoo)
ENV LANG=C.UTF-8

# Recuperar arquitectura para descargar wkhtmltopdf correcto
ARG TARGETARCH

# Instalar dependencias mínimas, Node (para less/rtlcss), wkhtmltopdf y cliente de PostgreSQL
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        dirmngr \
        fonts-noto-cjk \
        gnupg \
        libssl-dev \
        node-less \
        npm \
        python3-magic \
        python3-num2words \
        python3-odf \
        python3-pdfminer \
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
        git \
        build-essential \
        python3-dev \
        postgresql-client && \
    if [ -z "${TARGETARCH}" ]; then \
        TARGETARCH="$(dpkg --print-architecture)"; \
    fi; \
    WKHTMLTOPDF_ARCH=${TARGETARCH} && \
    case ${TARGETARCH} in \
      "amd64") WKHTMLTOPDF_ARCH=amd64 && WKHTMLTOPDF_SHA=9df8dd7b1e99782f1cfa19aca665969bbd9cc159  ;; \
      "arm64") WKHTMLTOPDF_SHA=58c84db46b11ba0e14abb77a32324b1c257f1f22  ;; \
      "ppc64le" | "ppc64el") WKHTMLTOPDF_ARCH=ppc64el && WKHTMLTOPDF_SHA=7ed8f6dcedf5345a3dd4eeb58dc89704d862f9cd  ;; \
    esac && \
    curl -o wkhtmltox.deb -sSL "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bullseye_${WKHTMLTOPDF_ARCH}.deb" && \
    echo "${WKHTMLTOPDF_SHA}  wkhtmltox.deb" | sha1sum -c - && \
    apt-get install -y --no-install-recommends ./wkhtmltox.deb && \
    rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# Instalar rtlcss globalmente (necesario para estilos RTL)
RUN npm install -g rtlcss

# Instalar Odoo 16.0
ENV ODOO_VERSION=16.0
ARG ODOO_RELEASE=20250604
RUN curl -o odoo.deb -sSL "http://nightly.odoo.com/${ODOO_VERSION}/nightly/deb/odoo_${ODOO_VERSION}.${ODOO_RELEASE}_all.deb" && \
    apt-get update && \
    apt-get -y install --no-install-recommends ./odoo.deb && \
    rm -rf /var/lib/apt/lists/* odoo.deb

# Ajustar UID/GID de usuario odoo para que sea 1100
RUN groupmod -g 1100 odoo && \
    usermod -u 1100 -g 1100 odoo

# Copiar entrypoint y configuración de Odoo
COPY ./entrypoint.sh /
COPY ./odoo.conf /etc/odoo/

# Crear directorios, permisos para filestore y addons de usuario
RUN chown odoo /etc/odoo/odoo.conf && \
    mkdir -p /mnt/extra-addons && \
    chown -R odoo /mnt/extra-addons
VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]

# Exponer puertos de Odoo
EXPOSE 8069 8071 8072

ENV ODOO_RC=/etc/odoo/odoo.conf

COPY wait-for-psql.py /usr/local/bin/wait-for-psql.py

USER odoo
ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]


# ----------------------------------------------------------------------
# Etapa 2: Capa superior para instalación de dependencias Adicionales
# ----------------------------------------------------------------------
FROM base-image
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

ENV ETC_DIR=/opt/odoo/etc
ENV DATA_DIR=/opt/odoo/data
ENV LOG_DIR=/var/log/odoo
ENV BKP_DIR=/var/odoo/backups
ENV ADDONS_DIR=/opt/odoo/custom-addons
ENV ODOO_RC=${ETC_DIR}/odoo.conf

# Crear directorios de configuración/datos/logs/backups/addons
RUN mkdir -p ${ETC_DIR} ${DATA_DIR} ${LOG_DIR} ${BKP_DIR} ${ADDONS_DIR} && \
    chown -R odoo:odoo /opt/odoo && \
    chown -R odoo:odoo /var/odoo

# Instalar pip (ya hay python3.10) y dependencias Python que queden por fuera de apt
RUN curl -fsSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py

# Copiar requirements y instalarlas
COPY ./requirements /req
RUN pip3 install -r /req/requirements.txt && \
    pip3 install -r /req/odoo-argentina.txt && \
    rm -r /req

# Crear cache para pyafipws (Python 3.10 usa /usr/local/lib/python3.10/)
RUN mkdir -p /usr/local/lib/python3.10/dist-packages/pyafipws/cache && \
    chmod -R 777 /usr/local/lib/python3.10/dist-packages/pyafipws

# Ajuste de cifrado para AFIP (bajar nivel de seguridad)
RUN sed -i "s/CipherString = DEFAULT@SECLEVEL=2/CipherString = DEFAULT@SECLEVEL=1/" /etc/ssl/openssl.cnf

USER odoo
