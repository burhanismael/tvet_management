# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SchoolSemester(models.Model):
    _name = "school.semester"
    _rec_name = 'semester_name'
    _description = "School Semester"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    semester_name = fields.Char(string="Semester", tracking=True)
    sem_number = fields.Integer(string="Sequence", tracking=True)
    # school_shift_id = fields.Many2one('school.shift', string=" Class Name")
    class_id = fields.Many2one('class.room', string="Class Name", tracking=True)
    academic_year_id = fields.Many2one('academic.year', string="Academic Year", tracking=True)

    @api.constrains('semester_name', 'class_id', 'academic_year_id')
    def _check_duplicate(self):
        if self.semester_name and self.class_id and self.academic_year_id:
            semester_id = self.env['school.semester'].search(
                [
                    ('semester_name', '=', self.semester_name),
                    ('class_id', '=', self.class_id.id),
                    ('academic_year_id', '=', self.academic_year_id.id)
                ]
            )
            if len(semester_id) > 1:
                raise ValidationError(_('Already available'))
