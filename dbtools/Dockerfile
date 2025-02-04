FROM python:3.12-alpine
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

# Instalar dependencias
RUN apk add --no-cache \
            postgresql-client \
            ca-certificates \
            gnupg \
            zip \
            unzip && \
    pip install --no-cache-dir psycopg2-binary==2.9.10 pytz==2024.2

# Establecer directorio de trabajo
WORKDIR /app

ADD dbtools.py .

# Configurar el script como punto de entrada
ENTRYPOINT ["python", "/app/dbtools.py"]
