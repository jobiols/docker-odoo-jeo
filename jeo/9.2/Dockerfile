FROM jobiols/odoo-jeo:9.1
MAINTAINER Jobiols <jorge.obiols@gmail.com>

USER root

COPY ./requirements /req
RUN pip install -r /req/requirements.txt
RUN cd req/hashlib-20081119 && export CC=gcc-5 && python setup.py build && sudo python setup.py install

USER odoo
