# terminado      1.82GB
# quitar el .git 1.65GB
# 1.93GB

################################################################################
# Etapa 1: Builder - Compilar Python y preparar dependencias de compilación
################################################################################
FROM debian:bullseye-slim AS builder
ARG PYTHON_VERSION=3.10.12
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/opt/python/bin:${PATH}"

# --- PASO 1.1: Instalar TODAS las dependencias de compilación de una vez ---
# - Dependencias para compilar Python.
# - Dependencias para compilar los paquetes de Python de Odoo (lxml, psycopg2, etc.).
# - Cliente de PostgreSQL para tener las cabeceras correctas.
# - git para clonar Odoo.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        # Para compilar Python
        build-essential curl ca-certificates libssl-dev zlib1g-dev \
        libbz2-dev libreadline-dev libsqlite3-dev libffi-dev \
        libncursesw5-dev xz-utils tk-dev \
        # Para compilar dependencias de Odoo
        libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libev-dev libpq-dev swig \
        # Para clonar el repo de Odoo
        git

# --- PASO 1.2: Compilar Python
WORKDIR /tmp
RUN curl -SL https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz | tar -xz && \
    cd Python-${PYTHON_VERSION} && \
    ./configure --prefix=/opt/python --enable-optimizations --with-ensurepip=install && \
    make -j"$(nproc)" && \
    make altinstall

# --- PASO 1.3: Clonar Odoo y construir un venv con las dependencias ---
# Usamos un Virtual Environment para instalar las dependencias de Odoo.
# Esto nos permite copiar solo los paquetes instalados a la etapa final,
# sin necesidad de tener las herramientas de compilación en la imagen final.
# además estamos eliminando el .git para reducir el tamaño de la imagen final.
ENV ODOO_VERSION=16.0
RUN git clone --depth 1 --branch ${ODOO_VERSION} https://github.com/odoo/odoo.git /opt/odoo && \
    rm -rf /opt/odoo/.git

RUN python3.10 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    # Instalar Cython < 3.0 dentro del venv
    /opt/venv/bin/pip install --no-cache-dir "cython<3.0" && \
    # Instalar los requerimientos de odoo/odoo usando el venv
    /opt/venv/bin/pip install \
        --no-cache-dir \
        --no-build-isolation \
        -r /opt/odoo/requirements.txt

COPY ./requirements /req
RUN /opt/venv/bin/pip install \
    # Instalar los requerimientos adicionales de Odoo en el venv librerias de odoo argentina, etc
    --no-cache-dir \
    --no-build-isolation \
    -r /req/odoo-argentina.txt  \
    -r /req/odoo-argentina-ce.txt  \
    -r /req/adhoc-aeroo_reports.txt  \
    -r /req/requirements.txt

################################################################################
# Etapa 2: Final/Runtime - Imagen mínima para ejecutar Odoo
################################################################################
FROM debian:bullseye-slim
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
# El PATH debe apuntar al venv
ENV PATH="/opt/venv/bin:/opt/python/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# --- PASO 2.1: Instalar dependencias de RUNTIME de una sola vez ---
# - Solo librerías (.so) necesarias, no paquetes -dev.
# - Cliente de PostgreSQL del repositorio oficial de PG para consistencia.
# - wkhtmltopdf y otras herramientas.
RUN apt-get update && \
    # Herramientas básicas e instalación del repo de PG
    apt-get install -y --no-install-recommends gnupg ca-certificates curl && \
    echo 'deb http://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main' > /etc/apt/sources.list.d/pgdg.list && \
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg && \
    apt-get update && \
    # Instalar todo lo necesario para ejecutar
    apt-get install -y --no-install-recommends \
        # Dependencias de Python compilado
        libssl1.1 libffi7 libbz2-1.0 libreadline8 libsqlite3-0 libncursesw6 zlib1g xz-utils tk \
        # Dependencias de paquetes de Python (lxml, ldap, etc)
        libxml2 libxslt1.1 libldap-2.4-2 libsasl2-2 libev4 \
        # Cliente de PostgreSQL y su librería principal
        postgresql-client libpq5 \
        # Dependencias requeridas por wkhtmltox
        fontconfig libjpeg62-turbo xfonts-75dpi xfonts-base \
        # Otras herramientas
        npm fonts-noto-cjk git && \
    # Limpieza de apt
    rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/pgdg.list && \
    # Instalar rtlcss
    npm install -g rtlcss && npm cache clean --force

# --- PASO 2.2: Instalar wkhtmltopdf
# Este bloque ahora funcionará porque las dependencias ya están instaladas.
ARG TARGETARCH
SHELL ["/bin/bash", "-xo", "pipefail", "-c"]
RUN \
    if [ -z "${TARGETARCH}" ]; then TARGETARCH="$(dpkg --print-architecture)"; fi; \
    WKHTMLTOPDF_ARCH=${TARGETARCH} && \
    case ${TARGETARCH} in \
        "amd64") WKHTMLTOPDF_ARCH=amd64; WKHTMLTOPDF_SHA=9df8dd7b1e99782f1cfa19aca665969bbd9cc159 ;; \
        "arm64") WKHTMLTOPDF_SHA=58c84db46b11ba0e14abb77a32324b1c257f1f22 ;; \
        "ppc64le" | "ppc64el") WKHTMLTOPDF_ARCH=ppc64el; WKHTMLTOPDF_SHA=7ed8f6dcedf5345a3dd4eeb58dc89704d862f9cd ;; \
    esac && \
    curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bullseye_${WKHTMLTOPDF_ARCH}.deb && \
    echo "${WKHTMLTOPDF_SHA} wkhtmltox.deb" | sha1sum -c - && \
    # Este comando ahora debería tener éxito
    apt-get install -y --no-install-recommends ./wkhtmltox.deb && \
    rm wkhtmltox.deb

# --- PASO 2.3: Copiar los artefactos de la etapa builder ---
COPY --from=builder /opt/python /opt/python
COPY --from=builder /opt/odoo /usr/bin/odoo
COPY --from=builder /opt/venv /opt/venv

# --- PASO 2.4: Configuración del usuario Odoo
RUN groupadd -g 1100 odoo && \
    useradd -u 1100 -g odoo -m -s /bin/bash odoo

COPY ./entrypoint.sh /
COPY ./odoo.conf /etc/odoo/
COPY ./wait-for-psql.py /usr/local/bin/wait-for-psql.py

RUN chown odoo /etc/odoo/odoo.conf && \
    mkdir -p /mnt/extra-addons && \
    chown -R odoo /mnt/extra-addons

ENV ETC_DIR=/opt/odoo/etc
ENV DATA_DIR=/opt/odoo/data
ENV LOG_DIR=/var/log/odoo
ENV BKP_DIR=/var/odoo/backups
ENV ADDONS_DIR=/opt/odoo/custom-addons
ENV ODOO_RC=${ETC_DIR}/odoo.conf
RUN mkdir -p ${ETC_DIR} ${DATA_DIR} ${LOG_DIR} ${BKP_DIR} ${ADDONS_DIR} && \
    chown -R odoo:odoo /opt/odoo /var/odoo

VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]
EXPOSE 8069 8071 8072
ENV ODOO_RC=/etc/odoo/odoo.conf

# Set default user and entrypoint
USER odoo
ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
