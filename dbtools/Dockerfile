FROM alpine:3.14
LABEL Jorge Obiols <jorge.obiols@gmail.com>

RUN apk --update add postgresql-client
ADD restore.sh /usr/bin/restore.sh
ADD extend.sh /usr/bin/extend.sh
ADD deactivate.sql /
ADD extend.sql /

CMD "/usr/bin/restore.sh"
