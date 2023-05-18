FROM jobiols/odoo-jeo:16.0

USER root

# Hacer el parche para que funcione como esclavo
RUN sed -i  "s/from odoo.addons.base.models.ir_cron import ir_cron/from odoo.addons.cge_multiproc.models.multi import HrControl/" /usr/lib/python3/dist-packages/odoo/service/server.py
RUN sed -i  "s/ir_cron._process_jobs(db_name)/HrControl._acquire_job(db_name)/" /usr/lib/python3/dist-packages/odoo/service/server.py

USER odoo
