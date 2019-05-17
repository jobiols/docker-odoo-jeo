-- Script para desactivar base de datos

-- desactivar tareas cron
UPDATE ir_cron SET active = FALSE;

-- eliminar servidores de correo
DELETE FROM fetchmail_server;
DELETE FROM ir_mail_server;

-- desactivar licencia
DELETE FROM ir_config_parameter
WHERE
  key  = 'database.enterprise_code' or
  key = 'database.expiration_date' or
  key = 'database.expiration_reason';

-- eliminar contrasenas
UPDATE res_users
  SET password_crypt = NULL
WHERE id <> 1
