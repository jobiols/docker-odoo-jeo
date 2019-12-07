FROM debian:stretch-slim
MAINTAINER Jorge Obiols <jorge.obiols@gmail.com>

ENV UPDATED 2019-11-04

RUN DEBIAN_FRONTEND=noninteractive && \
        apt-get update && apt-get install -y \
    git \
    python3-uno \
    libreoffice-writer \
    libreoffice-calc \
    python3-pip \
    xvfb \
    supervisor \
    openjdk-8-jre

# Accept EULA for MS fonts
RUN echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections # Accept EULA for MS fonts

# agregamos fuentes solicitadas por ivan
RUN set -x; \
        apt-get update && apt-get install -y --no-install-recommends \
    msttcorefonts \
    curl \
    fonts-cantarell \
    ttf-mscorefonts-installer

RUN curl -s https://raw.githubusercontent.com/hotice/webupd8/master/install-google-fonts | bash

# este por ahora no es necesario y ademas pesa muchísimo
#RUN apt-get install -y ubuntustudio-font-meta
COPY ./resources/segoeui/ /usr/share/fonts/truetype/segoeui/

# Limpieza
#RUN apt-get clean

RUN pip3 install jsonrpc2
RUN pip3 install daemonize

RUN git clone https://github.com/aeroo/aeroo_docs.git /opt/aeroo_docs

EXPOSE 8989

ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD supervisord -c /etc/supervisor/conf.d/supervisord.conf

# adhoc 2.61
# ubuntu 1.2
# debian:stretch-slim 1.2