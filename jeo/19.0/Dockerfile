# Usa la imagen base de Ubuntu
FROM ubuntu:jammy
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Configuración de locale y versiones
ENV LANG=en_US.UTF-8
ENV ODOO_VERSION=19.0
ARG ODOO_RELEASE
ENV ODOO_RELEASE=${ODOO_RELEASE}

# --- NUEVO: Definir la ruta del entorno virtual y del home de Odoo ---
ENV ODOO_HOME=/odoo
ENV VENV_PATH=/odoo/venv

# --------------------------------------------------------------------------------------------------
# PASO 1: INSTALAR DEPENDENCIAS DEL SISTEMA (NO-PYTHON) Y WKHTMLTOPDF
# --------------------------------------------------------------------------------------------------
# Se han quitado todos los paquetes 'python3-*' de aquí. Serán instalados con pip.
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        dirmngr \
        fonts-noto-cjk \
        gnupg \
        libssl-dev \
        node-less \
        npm \
        python3-dev \
        build-essential \
        gcc \
        libpq-dev \
        libldap2-dev \
        libsasl2-dev \
        python3-pip \
        python3-venv \
        xz-utils \
        git && \
    TARGETARCH=${TARGETARCH:-$(dpkg --print-architecture)} && \
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

# --------------------------------------------------------------------------------------------------
# PASO 2: INSTALAR CLIENTE DE POSTGRESQL Y RTLSS (SIN CAMBIOS)
# --------------------------------------------------------------------------------------------------
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ jammy-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
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
RUN npm install -g rtlcss

# --------------------------------------------------------------------------------------------------
# PASO 3: CREAR USUARIO, ENTORNO VIRTUAL Y ACTIVARLO
# --------------------------------------------------------------------------------------------------
# Crear el usuario 'odoo' con UID y GID 1100, junto con su directorio home.
# Se utilizan estos IDs para que coincidan con los del usuario en el host,
# evitando conflictos de permisos al montar volúmenes desde el host hacia el contenedor.
RUN addgroup --gid 1100 odoo && \
    adduser --system --uid 1100 --gid 1100 \
    --shell /bin/bash --home ${ODOO_HOME} --gecos "ODOO" odoo

# Crear el entorno virtual como el usuario root, pero asignarlo al usuario odoo
RUN python3 -m venv ${VENV_PATH} && chown -R odoo:odoo ${VENV_PATH}
# Activar el venv para todas las instrucciones futuras. Esto es clave.
ENV PATH="${VENV_PATH}/bin:${PATH}"

# --------------------------------------------------------------------------------------------------
# PASO 4: INSTALAR TODAS LAS DEPENDENCIAS DE PYTHON DENTRO DEL VENV (ESTRATEGIA MULTI-PASO)
# --------------------------------------------------------------------------------------------------
# Actualizar pip para tener la última versión
RUN pip install --no-cache-dir --upgrade pip

# -- SUB-PASO 4.1: INSTALAR GEVENT CON HERRAMIENTAS ANTIGUAS --
# Instalar las versiones antiguas de las herramientas de construcción que gevent necesita
RUN pip install --no-cache-dir "Cython<3.0" "setuptools<60" wheel
# Instalar gevent y su dependencia directa, forzando a pip a usar las herramientas que acabamos de instalar
RUN pip install --no-cache-dir --no-build-isolation "gevent==21.8.0" "greenlet==1.1.2"

# -- SUB-PASO 4.2: ACTUALIZAR HERRAMIENTAS PARA EL RESTO DE PAQUETES --
# Ahora que lo antiguo está instalado, actualizamos las herramientas para los paquetes modernos
RUN pip install --no-cache-dir --upgrade setuptools wheel

# -- SUB-PASO 4.3: INSTALAR EL RESTO DE LOS REQUERIMIENTOS --
# Instalar dependencias que antes se instalaban con apt, ahora con pip
RUN pip install --no-cache-dir \
    python-magic \
    num2words \
    odfpy \
    pdfminer.six \
    phonenumbers \
    pyldap \
    qrcode \
    Pillow \
    reportlab \
    vobject \
    watchdog \
    xlrd \
    xlwt

#    python-slugify-unicode \

# Instalar Odoo
RUN git clone --depth 1 --branch ${ODOO_VERSION} https://www.github.com/odoo/odoo ${ODOO_HOME}/odoo-src
ENV PATH="${ODOO_HOME}/odoo-src:${PATH}"

# Instalar el resto de los requerimientos de Odoo Core.
# Pip ignorará gevent/greenlet porque ya están instalados.
# Usará las herramientas modernas que instalamos en el paso 4.2.
RUN pip install --no-cache-dir -r ${ODOO_HOME}/odoo-src/requirements.txt

# Instalar los requerimientos personalizados de tus addons
COPY ./requirements /req
RUN pip install --no-cache-dir -r /req/requirements.txt && rm -r /req

# --------------------------------------------------------------------------------------------------
# PASO 5: CONFIGURAR DIRECTORIOS, PERMISOS Y ENTRYPOINT
# --------------------------------------------------------------------------------------------------
# Definir variables de entorno para los directorios
ENV ETC_DIR=/opt/odoo/etc
ENV DATA_DIR=/opt/odoo/data
ENV LOG_DIR=/var/log/odoo
ENV BKP_DIR=/var/odoo/backups
ENV ADDONS_DIR=/opt/odoo/custom-addons
ENV ODOO_RC=${ETC_DIR}/odoo.conf
# Crear directorios. /opt/odoo se usa para configuraciones y datos, no para el código
RUN mkdir -p ${ETC_DIR} ${DATA_DIR} ${ADDONS_DIR} ${BKP_DIR} \
    && chown -R odoo:odoo /opt/odoo
# Crear directorio de logs
RUN mkdir -p ${LOG_DIR} && chown -R odoo:odoo ${LOG_DIR}
# Crear directorio de backups
RUN mkdir -p /var/odoo && chown -R odoo:odoo /var/odoo

# Copiar artefactos de configuración
COPY entrypoint.sh /
COPY odoo.conf $ETC_DIR/
COPY wait-for-psql.py /usr/local/bin/wait-for-psql.py
RUN chmod +x /entrypoint.sh /usr/local/bin/wait-for-psql.py

# Exponer puertos
EXPOSE 8069 8071 8072

# Cambiar al usuario final
USER odoo

# El entrypoint ahora usará el python y pip del venv gracias a la variable de entorno PATH
ENTRYPOINT ["/entrypoint.sh"]

# El comando se pasa desde docker-compose.yml
# CMD ["odoo-bin", "-c", "/opt/odoo/etc/odoo.conf"]