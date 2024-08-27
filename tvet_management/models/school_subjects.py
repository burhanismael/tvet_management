# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SchoolSubjects(models.Model):
    _name = "school.subject"
    _rec_name = 'name'
    _description = "TVET School Subject"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Subject", tracking=True)
    subject_code = fields.Char(string="Subject Code")
    credit_hrs = fields.Char(string="Credit Hours", tracking=True)
    remarks = fields.Text(string="Remarks", tracking=True)

    @api.constrains('name')
    def _check_duplicate(self):
        if self.name:
            subject_id = self.env['school.subject'].search(
                [
                    ('name', '=', self.name)
                ]
            )
            if len(subject_id) > 1:
                raise ValidationError(_('Subject is already available'))
