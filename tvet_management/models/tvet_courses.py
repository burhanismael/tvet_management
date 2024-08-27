# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SchoolCourse(models.Model):
    _name = "school.course"
    _rec_name = 'name'
    _description = "TVET Course"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Course", tracking=True)
    department_id = fields.Many2one('tvet.department', string="Department Name", tracking=True)
    remarks = fields.Text(string="Remarks", tracking=True)

    @api.constrains('name')
    def _check_duplicate(self):
        if self.name:
            course_id = self.env['school.course'].search(
                [
                    ('name', '=', self.name)
                ]
            )
            if len(course_id) > 1:
                raise ValidationError(_('Course is already available'))
