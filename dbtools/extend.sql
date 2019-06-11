-- Script para extender la licencia de la base de datos, no muestra el cartel de vencimiento

UPDATE ir_config_parameter
SET
  value = 'trial'
WHERE
  key = 'database.expiration_reason';

UPDATE ir_config_parameter
SET
  value = '2019-07-23 00:00:00'
WHERE
  key = 'database.expiration_date';

DELETE FROM ir_config_parameter
WHERE
  key = 'database.enterprise_code';
