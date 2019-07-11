delete from ir_config_parameter
where key = 'database.enterprise_code';

update ir_config_parameter
set value = 'trial'
where key = 'database.expiration_reason';

update ir_config_parameter
set value = current_date + integer '30'
where key = 'database.expiration_date';
