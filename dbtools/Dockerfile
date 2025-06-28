FROM python:3.12-alpine
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

# Instalar dependencias
# postgresql-client en Alpine incluye pg_dump, psql, pg_restore, pg_dumpall
RUN apk add --no-cache \
            postgresql-client \
            ca-certificates \
            gnupg \
            zip \
            unzip

RUN pip install --no-cache-dir \
    psycopg2-binary==2.9.10 \
    pytz==2025.2

# Establecer directorio de trabajo
WORKDIR /app

COPY dbtools.py .

# Configurar el script como punto de entrada
ENTRYPOINT ["python", "/app/dbtools.py"]