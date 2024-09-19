# -- coding: utf-8 --
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools
from odoo.exceptions import ValidationError


class BaseModuleUninstall(models.TransientModel):
    _inherit = "base.module.uninstall"

    def action_uninstall(self):
        raise ValidationError("You can not Uninstall This Modules")
        return super(BaseModuleUninstall, self).action_uninstall()
