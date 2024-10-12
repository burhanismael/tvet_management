# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class TestimonialGraduationWizard(models.TransientModel):
    _name = "testimonial.graduation.report"
    _description = 'Testimonial Graduation Wizard'

    student_id = fields.Many2one('student.registration', string="Student Name", required=True)
    class_id = fields.Many2one('class.room', string="Class Name", required=True)
    date = fields.Date(string='Certificate Issuance Date')

    def pdf_report(self):
        record_data = {
            'class_id': self.class_id.id,
            'student_id': self.student_id,
            'c_date': self.date,
        }
        return self.env.ref('tvet_management.action_testimonial_graduation_report').report_action(self, data=record_data)

    def pdf_preview_report(self):
        record_data = {
            'class_id': self.class_id.id,
            'student_id': self.student_id,
            'c_date': self.date,
        }
        return self.env.ref('tvet_management.action_testimonial_graduation_preview_report').report_action(self, data=record_data)


    @api.onchange('class_id')
    def class_based_domain(self):
        student_ids = self.env['student.registration'].search([('classroom_id', '=', self.class_id.id), ('status', '=', 'enrolled')])
        domain = [('id', 'in', student_ids.ids)]
        return {'domain': {'student_id': domain}}