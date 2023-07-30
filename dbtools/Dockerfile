FROM debian:bullseye-slim
LABEL Jorge Obiols <jorge.obiols@gmail.com>

RUN apt-get update \
        && apt-get install -y --no-install-recommends \
            ca-certificates \
            dirmngr \
            fonts-noto-cjk \
            gnupg \
            python3-pip \
            zip \
            unzip
            # libssl-dev \
            # node-less \
            # python3-num2words \
            # python3-phonenumbers \
            # python3-pyldap \
            # python3-qrcode \
            # python3-renderpm \
            # python3-setuptools \
            # python3-slugify \
            # python3-vobject \
            # python3-watchdog \

    RUN pip install psycopg2-binary


# install latest postgresql-client
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
    && GNUPGHOME="$(mktemp -d)" \
    && export GNUPGHOME \
    && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \
    && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \
    && gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \
    && gpgconf --kill all \
    && rm -rf "$GNUPGHOME" \
    && apt-get update  \
    && apt-get install --no-install-recommends -y postgresql-client-15 \
    && rm -f /etc/apt/sources.list.d/pgdg.list \
    && rm -rf /var/lib/apt/lists/*

ADD dbtools.py /dbtools.py
ADD extend.sh /usr/bin/extend.sh
ADD deactivate.sql /
ADD extend.sql /

ENTRYPOINT ["/dbtools.py"]
