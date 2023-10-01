-- Script para neutralizar base de datos, si es EE la vuelve trial con un mes de uso.

-- desactivar tareas cron
-- UPDATE ir_cron SET active = FALSE;

-- eliminar servidores de correo
DELETE FROM fetchmail_server;
DELETE FROM ir_mail_server;

-- desactivar licencia
DELETE FROM ir_config_parameter
WHERE
  key  = 'database.enterprise_code' or
  key = 'database.expiration_date' or
  key = 'database.expiration_reason';

-- cambiar la contraseña de admin
UPDATE res_users
SET login = 'admin', password = 'admin'
WHERE id = 2;

-- end of neutralization
