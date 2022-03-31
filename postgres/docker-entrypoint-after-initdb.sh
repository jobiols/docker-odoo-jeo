#!/usr/bin/env bash
mkdir -p ${PGDATA}/conf.d && \
sed -i '/^# "local".*/a local\todoo\t\todoo\t\t\t\t\tmd5' "${PGDATA}/pg_hba.conf" && \
sed -i "s/#include_dir = '...'/include_dir = 'conf.d'/" "${PGDATA}/postgresql.conf" && \
cp -f /docker-entrypoint-initdb.d/*.conf ${PGDATA}/conf.d && \
chown -R postgres:postgres ${PGDATA}/conf.d && \
chmod -R 777 ${PGDATA}/conf.d
