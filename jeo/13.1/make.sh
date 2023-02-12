#!/usr/bin/env bash
sd build --rm=true -t jobiols/odoo-jeo:13.1 ./
sd push jobiols/odoo-jeo:13.1
