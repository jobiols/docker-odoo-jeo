FROM python:3.11-alpine
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

# Instalar dependencias
RUN apk add --no-cache \
            postgresql-client \
            ca-certificates \
            gnupg \
            zip \
            unzip

# Instalar paquetes de Python
RUN pip install --no-cache-dir psycopg2-binary pytz

ADD dbtools.py /dbtools.py

# Crear usuario
RUN addgroup -g 1100 appgroup && \
    adduser -D -u 1100 -G appgroup odoo

USER 1100:1100

ENTRYPOINT ["/dbtools.py"]