# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResCity(models.Model):
    _name = "res.state"
    _rec_name = 'name'
    _description = "City Information"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="State", tracking=True)

    @api.constrains('name')
    def _check_duplicate(self):
        if self.name:
            city_id = self.env['res.state'].search(
                [
                    ('name', '=', self.name)
                ]
            )
            if len(city_id) > 1:
                raise ValidationError(_('City is already available'))