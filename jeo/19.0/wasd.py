from functools import wraps
from odoo import _, exceptions


def restrict_milestone(milestone_key):
    """
    Decorador para restringir funciones según hitos.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            is_active = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(f"milestone.{milestone_key}", default="false")
            )

            if is_active != "true":
                raise exceptions.UserError(
                    _(
                        "Esta funcionalidad corresponde al hito '%s' y aún no ha sido aprobada/activada."
                    )
                    % milestone_key
                )

            return func(self, *args, **kwargs)

        return wrapper

    return decorator