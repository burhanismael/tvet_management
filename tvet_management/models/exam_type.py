# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ExamType(models.Model):
    _name = "exam.type"
    _rec_name = 'exam_type'
    _description = "Exam Type Information"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    exam_type = fields.Char(string="Exam Type", tracking=True)
    required_mark = fields.Float(string="Required Marks", tracking=True)
    maximum_mark = fields.Float(string="Maximum Marks", tracking=True)
    remarks = fields.Text(string="Remarks", tracking=True)
    is_portal = fields.Boolean(string="Is Display In Portal", tracking=True)

    @api.constrains('exam_type')
    def _check_duplicate(self):
        if self.exam_type:
            exam_type_id = self.env['exam.type'].search(
                [
                    ('exam_type', '=', self.exam_type),
                ]
            )
            if len(exam_type_id) > 1:
                raise ValidationError(_('Exam already available'))
