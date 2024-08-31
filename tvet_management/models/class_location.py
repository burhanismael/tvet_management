# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ClassLocation(models.Model):
    _name = "class.location"
    _rec_name = 'location'
    _description = " Information"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    section = fields.Char(string="Section Name", tracking=True)
    location = fields.Char(string="Location Name", tracking=True)

    @api.constrains('section', 'location')
    def _check_duplicate(self):
        if self.section and self.location:
            location_id = self.env['class.location'].search(
                [
                    ('section', '=', self.section),
                    ('location', '=', self.location)
                ]
            )
            if len(location_id) > 1:
                raise ValidationError(_('Already available'))
