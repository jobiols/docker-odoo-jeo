--Neutralizar la base de datos

con esto se puede obtener los archivos sql de la neutralizacion
sudo docker exec -it odoo find -name neutralize.sql


SELECT name
FROM
  ir_module_module
WHERE
  state IN ('installed', 'to upgrade', 'to remove');
