# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CourseSubject(models.Model):
    _name = "course.subject"
    _rec_name = 'course_name'
    _description = "Course Information"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    course_code = fields.Char(string="Course Code", tracking=True)
    course_name = fields.Char(string="Course Name", tracking=True)
    credit_hrs = fields.Float(string="Credit Hrs", tracking=True)
    is_medical = fields.Boolean(string="Medicine", tracking=True)
    department_id = fields.Many2one('school.department', string=" Department Name")
    remarks = fields.Text(string="Remarks", tracking=True)
    school_department_id = fields.Many2one('school.department', string="Department Name", tracking=True)

    @api.constrains('course_code')
    def _check_duplicate(self):
        if self.course_code:
            course_id = self.env['course.subject'].search(
                [
                    ('course_code', '=', self.course_code)
                ]
            )
            if len(course_id) > 1:
                raise ValidationError(_('Course code already available'))
