FROM debian:stretch-slim
MAINTAINER Jorge Obiols <jorge.obiols@gmail.com>

RUN set -x; \
        apt-get update \
        && apt-get install -y --no-install-recommends \
            dirmngr \
            unzip \
            gnupg

# install latest postgresql-client
RUN set -x; \
        echo 'deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main' > etc/apt/sources.list.d/pgdg.list \
        && export GNUPGHOME="$(mktemp -d)" \
        && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \
        && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \
        && gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \
        && gpgconf --kill all \
        && rm -rf "$GNUPGHOME" \
        && apt-get update  \
        && apt-get install -y postgresql-client \
        && rm -rf /var/lib/apt/lists/*

ADD restore.sh /usr/bin/restore.sh
ADD extend.sh /usr/bin/extend.sh
ADD deactivate.sql /
ADD extend.sql /

CMD "/usr/bin/restore.sh"
