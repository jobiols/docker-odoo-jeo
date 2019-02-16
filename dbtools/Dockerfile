FROM debian:jessie
MAINTAINER Jorge Obiols <jorge.obiols@gmail.com>

# actualizar las sources.list con el repo de postgress
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main" >  /etc/apt/sources.list.d/pgdg.list

# actualizar e instalar wget
RUN apt-get update && apt-get install wget unzip -y

# traerme las keys e instalarlas
#RUN apt-get install ca-certificates -y
#RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

# instalar postgress client
RUN apt-get update && apt-get install postgresql-client-9.4 -y --force-yes --no-install-recommends

ADD restore.sh /usr/bin/restore.sh
ADD deactivate.sql /

CMD "/usr/bin/restore.sh"
