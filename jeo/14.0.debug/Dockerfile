FROM jobiols/odoo-jeo:14.0
LABEL maintainer="Jorge Obiols <jorge.obiols@gmail.com>"

USER root

# scripts to extract sources to host
COPY ./extract_dist-packages.sh /
COPY ./extract_dist-local-packages.sh /

# install wdb
RUN pip3 install wdb

# Correr un demonio para atrapar los mails.
RUN python3 -m smtpd -n -c DebuggingServer localhost:2500 >  /var/log/odoo/maillog.txt &

USER odoo
