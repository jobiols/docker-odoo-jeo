-- Script para desactivar base de datos

-- desactivar tareas cron
UPDATE ir_cron SET active = FALSE;

-- desactivar servidores de correo
DELETE FROM fetchmail_server;
DELETE FROM ir_mail_server;
