FROM debian:stretch

RUN set -x; \
        apt-get update \
        && apt-get install -y --no-install-recommends \
            ca-certificates \
            wget \
            dirmngr \
            gnupg


#RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main' >  /etc/apt/sources.list.d/pgdg.list
#RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
#RUN apt-get update
#RUN yes Y | apt-get install postgresql-client-11
#RUN rm -rf /var/lib/apt/lists/*


RUN       echo 'deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main' > etc/apt/sources.list.d/pgdg.list \
        && export GNUPGHOME="$(mktemp -d)" \
        && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \
        && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \
        && gpg --armor --export "${repokey}" | apt-key add - \
        && gpgconf --kill all \
        && rm -rf "$GNUPGHOME" \
        && apt-get update  \
        && apt-get install -y postgresql-client-11 \
        && rm -rf /var/lib/apt/lists/*
