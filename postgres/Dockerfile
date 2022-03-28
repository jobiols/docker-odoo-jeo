FROM postgres:14.2
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>, Martin Llanos <martinllanos@gmail.com>"

ARG PARTMAN_VERSION=4.6.0
ARG PG_DEV_VERSION=14

RUN set -x \
	&& apt-get update && apt-get install -y --no-install-recommends ca-certificates wget \
    unzip make postgresql-server-dev-$PG_DEV_VERSION \
    gcc libc6-dev libssl-dev libkrb5-dev \
    && wget -O /tmp/pg_partman.zip https://github.com/pgpartman/pg_partman/archive/refs/tags/v$PARTMAN_VERSION.zip \
	&& unzip /tmp/pg_partman.zip  -d /tmp \
    && cd /tmp/pg_partman-$PARTMAN_VERSION \
    && make install \
    && rm -rf /var/lib/apt/lists/* && apt-get purge -y --auto-remove ca-certificates wget unzip make postgresql-server-dev-$PG_DEV_VERSION gcc libc6-dev libssl-dev libkrb5-dev \
    && rm -rf /tmp/pg_*

COPY docker-entrypoint-initdb.d/* /docker-entrypoint-initdb.d/
COPY docker-entrypoint-after-initdb.sh /docker-entrypoint-initdb.d/0-docker-entrypoint-after-initdb.sh