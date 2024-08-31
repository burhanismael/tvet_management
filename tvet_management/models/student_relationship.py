# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StudentRelationship(models.Model):
    _name = "student.relationship"
    _rec_name = 'name'
    _description = "Student Relationship Information"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Relationship with the Student", tracking=True)

    @api.constrains('name')
    def _check_duplicate(self):
        if self.name:
            relationship_id = self.env['student.relationship'].search(
                [
                    ('name', '=', self.name)]
            )
            if len(relationship_id) > 1:
                raise ValidationError(_('Relationship is already available'))
