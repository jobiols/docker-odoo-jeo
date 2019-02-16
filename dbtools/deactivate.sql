-- Script para desactivar base de datos

-- desactivar tareas cron
UPDATE ir_cron SET active = FALSE;

-- desactivar servidores de correo
UPDATE fetchmail_server SET active = FALSE;
UPDATE ir_mail_server SET active = FALSE;
