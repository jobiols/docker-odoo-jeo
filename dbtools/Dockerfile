# Start from debian 12 Bookworm
#FROM debian:bookworm-slim
FROM python:3.11-slim
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

# Configurar el entorno para no interactuar con la instalación
#ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg2 \
    lsb-release \
#    python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Agregar el repositorio de PostgreSQL y su clave
RUN echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

# Instalar el cliente de PostgreSQL
RUN apt-get update && apt-get install -y postgresql-client-15 \
    && rm -rf /var/lib/apt/lists/*

#RUN pip install pytz requests
#RUN pip install Werkzeug
RUN pip3 install psycopg2-binary pytz

ADD dbtools.py /dbtools.py
#ADD neutralize.sql /
#ADD extend.sql /

ENTRYPOINT ["/dbtools.py"]
