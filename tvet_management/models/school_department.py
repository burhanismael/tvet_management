# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SchoolDepartment(models.Model):
    _name = "school.department"
    _rec_name = 'name'
    _description = "Department Information"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Department", tracking=True)
    department_code = fields.Char('Department Code', tracking=True)
    remarks = fields.Text(string="Remarks", tracking=True)

    @api.constrains('name')
    def _check_duplicate(self):
        if self.name:
            department_id = self.env['school.department'].search(
                [
                    ('name', '=', self.name)
                ]
            )
            if len(department_id) > 1:
                raise ValidationError(_('Department is already available'))
