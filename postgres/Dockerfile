FROM postgres:14.2
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

ARG PATHMAN_VERSION=1.5.12
ARG PG_DEV_VERSION=14

RUN set -x \
	&& apt-get update && apt-get install -y --no-install-recommends ca-certificates wget \
    unzip make postgresql-server-dev-$PG_DEV_VERSION \
    gcc libc6-dev libssl-dev libkrb5-dev libxml2-dev libxml2 \
    && wget -O /tmp/pg_pathman.zip https://github.com/postgrespro/pg_pathman/archive/$PATHMAN_VERSION.zip \
	&& unzip /tmp/pg_pathman.zip  -d /tmp \
    && cd /tmp/pg_pathman-$PATHMAN_VERSION \
    && make USE_PGXS=1 install \
    && rm -rf /var/lib/apt/lists/* && apt-get purge -y --auto-remove ca-certificates wget unzip make postgresql-server-dev-$PG_DEV_VERSION gcc libc6-dev libssl-dev libkrb5-dev \
    && rm -rf /tmp/pg_*

COPY docker-entrypoint-initdb.d/* /docker-entrypoint-initdb.d/
COPY docker-entrypoint-after-initdb.sh /docker-entrypoint-initdb.d/0-docker-entrypoint-after-initdb.sh
