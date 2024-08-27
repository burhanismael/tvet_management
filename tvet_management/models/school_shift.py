# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SchoolShift(models.Model):
    _name = "school.shift"
    _rec_name = 'name'
    _description = "School Shift Information"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Shift", tracking=True)
    school_department_id = fields.Many2one('tvet.department', string="Department Name", tracking=True)

    @api.constrains('name', 'school_department_id')
    def _check_duplicate(self):
        if self.name and self.school_department_id:
            shift_id = self.env['school.shift'].search(
                [
                    ('name', '=', self.name),
                    ('school_department_id', '=', self.school_department_id.id),
                ]
            )
            if len(shift_id) > 1:
                raise ValidationError(_('Already available'))
