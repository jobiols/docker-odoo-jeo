FROM jobiols/odoo-jeo:11.0
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

# scripts to extract sources to host
COPY ./extract_dist-packages.sh /
COPY ./extract_dist-local-packages.sh /

# requerimiento para odoo-uml
RUN apt-get -qq update && apt-get install -yqq --no-install-recommends \
    default-jdk \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install \
    wdb \
    erppeek

# Hacer el parche para que no cheque password
RUN sed -i  "s/raise AccessDenied()/pass/" /usr/lib/python3/dist-packages/odoo/addons/base/res/res_users.py

# Correr un demonio para atrapar los mails.
RUN python3 -m smtpd -n -c DebuggingServer localhost:2500 >  /var/log/odoo/maillog.txt &

USER odoo
