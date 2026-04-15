# Usa la imagen base de Ubuntu 24.04 (Noble)
FROM ubuntu:noble
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Configuración de locale y versiones
ENV LANG=en_US.UTF-8
ENV ODOO_VERSION=19.0
ARG ODOO_RELEASE
ENV ODOO_RELEASE=${ODOO_RELEASE}

# Definir la ruta del entorno virtual y del home de Odoo
ENV ODOO_HOME=/odoo
ENV VENV_PATH=/odoo/venv

# --------------------------------------------------------------------------------------------------
# PASO 1: INSTALAR DEPENDENCIAS DEL SISTEMA
# --------------------------------------------------------------------------------------------------
# Nota: Ubuntu 24.04 usa libssl3 por defecto.
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
    # Instalación de WKHTMLTOPDF (usamos la versión de Jammy ya que es compatible con Noble en SSL3)
    TARGETARCH=${TARGETARCH:-$(dpkg --print-architecture)} && \
    WKHTMLTOPDF_ARCH=${TARGETARCH} && \
    case ${TARGETARCH} in \
    "amd64") WKHTMLTOPDF_ARCH=amd64 && WKHTMLTOPDF_SHA=967390a759707337b46d1c02452e2bb6b2dc6d59  ;; \
    "arm64")  WKHTMLTOPDF_SHA=90f6e69896d51ef77339d3f3a20f8582bdf496cc  ;; \
    esac \
    && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.jammy_${WKHTMLTOPDF_ARCH}.deb \
    && echo ${WKHTMLTOPDF_SHA} wkhtmltox.deb | sha1sum -c - \
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# --------------------------------------------------------------------------------------------------
# PASO 2: INSTALAR CLIENTE DE POSTGRESQL (Ajustado para Noble)
# --------------------------------------------------------------------------------------------------
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ noble-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
    && curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg \
    && apt-get update  \
    && apt-get install --no-install-recommends -y postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g rtlcss

# --------------------------------------------------------------------------------------------------
# PASO 3: CREAR USUARIO Y ENTORNO VIRTUAL
# --------------------------------------------------------------------------------------------------
RUN addgroup --gid 1100 odoo && \
    adduser --system --uid 1100 --gid 1100 \
    --shell /bin/bash --home ${ODOO_HOME} --gecos "ODOO" odoo

# En Ubuntu 24.04, es obligatorio usar venv para instalar paquetes pip fuera del sistema
RUN python3 -m venv ${VENV_PATH} && chown -R odoo:odoo ${VENV_PATH}
ENV PATH="${VENV_PATH}/bin:${PATH}"

# --------------------------------------------------------------------------------------------------
# PASO 4: INSTALAR DEPENDENCIAS DE PYTHON (LIMPIO)
# --------------------------------------------------------------------------------------------------
# 4.1 Actualizar Pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 4.2 Instalar dependencias extra necesarias para muchos módulos de Odoo
RUN pip install --no-cache-dir \
    python-magic \
    num2words \
    odfpy \
    pdfminer.six \
    phonenumbers \
    python-ldap \
    qrcode \
    Pillow \
    reportlab \
    vobject \
    watchdog \
    xlrd \
    xlwt

# 4.3 Clonar Odoo 19
RUN git clone --depth 1 --branch ${ODOO_VERSION} https://www.github.com/odoo/odoo ${ODOO_HOME}/odoo-src
ENV PATH="${ODOO_HOME}/odoo-src:${PATH}"

# 4.4 Instalar los requerimientos de Odoo Core.
# En Noble/Python 3.12, cbor2 y gevent se instalarán sin errores.
RUN pip install --no-cache-dir -r ${ODOO_HOME}/odoo-src/requirements.txt

# 4.5 Requerimientos adicionales del usuario
COPY ./requirements /req
RUN if [ -f /req/requirements.txt ]; then pip install --no-cache-dir -r /req/requirements.txt; fi && rm -rf /req

# --------------------------------------------------------------------------------------------------
# PASO 5: CONFIGURAR DIRECTORIOS, PERMISOS Y ENTRYPOINT
# --------------------------------------------------------------------------------------------------
ENV ETC_DIR=/opt/odoo/etc
ENV DATA_DIR=/opt/odoo/data
ENV LOG_DIR=/var/log/odoo
ENV BKP_DIR=/var/odoo/backups
ENV ADDONS_DIR=/opt/odoo/custom-addons
ENV ODOO_RC=${ETC_DIR}/odoo.conf

RUN mkdir -p ${ETC_DIR} ${DATA_DIR} ${ADDONS_DIR} ${BKP_DIR} ${LOG_DIR} /var/odoo \
    && chown -R odoo:odoo /opt/odoo ${LOG_DIR} /var/odoo ${ODOO_HOME}

# Copiar artefactos
COPY entrypoint.sh /
COPY odoo.conf $ETC_DIR/
COPY wait-for-psql.py /usr/local/bin/wait-for-psql.py
RUN chmod +x /entrypoint.sh /usr/local/bin/wait-for-psql.py

# copiar el decorador wasd que funcionará solo para sulh
COPY wasd.py ${ODOO_HOME}/odoo-src/odoo/
#RUN echo "from . import wasd" >> ${ODOO_HOME}/odoo-src/odoo/init.py
#RUN chown -R odoo.odoo ${ODOO_HOME}/odoo-src/odoo/wasd.py

EXPOSE 8069 8071 8072

USER odoo

ENTRYPOINT ["/entrypoint.sh"]