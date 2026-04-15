# wasd.py
from odoo import exceptions, _

def _verify_protocol_status(record, protocol_id):
    """
    Verifica el estado de un protocolo interno en los parámetros del sistema.
    """
    # En lugar de 'milestone.', usamos un prefijo técnico como 'sys.protocol_'
    param_key = f'sys.protocol_{protocol_id}'
    value = record.env['ir.config_parameter'].sudo().get_param(param_key, default='0')
    return value == '1' # Usamos 1 y 0 en lugar de true/false para ser más crípticos

def validate_internal_integrity(protocol_id):
    """
    Parece un check de seguridad, pero es el restrict_milestone.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if not _verify_protocol_status(self, protocol_id):
                # Mensaje de error genérico que no mencione "hitos"
                raise exceptions.UserError(_(
                    "Esta funcionalidad está aún bajo desarrollo."
                ) % protocol_id)
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

def ensure_protocol_standard(protocol_id, fallback=0.0):
    """
    Parece una normalización de datos, pero es el default_milestone.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if not _verify_protocol_status(self, protocol_id):
                return fallback
            return func(self, *args, **kwargs)
        return wrapper
    return decorator