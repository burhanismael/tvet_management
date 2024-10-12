# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class TestimonialContinuesWizard(models.TransientModel):
    _name = "testimonial.continues.report"
    _description = 'Testimonial Continues Wizard'

    class_id = fields.Many2one('class.room', string="Class Name", required=True)
    # semister_id = fields.Many2one('semester.semester', string="Semester Name", required=True)
    student_id = fields.Many2one('student.registration', string="Student Name")
    # date = fields.Date(string='Certificate Issuance Date')


    def pdf_report(self):
        record_data = {
            'class_id': self.class_id.id,
            # 'semister_id': self.semister_id.id,
            'student_id': self.student_id.id,
        }
        return self.env.ref('tvet_management.action_testimonial_continues_report').report_action(self, data=record_data)

    def pdf_preview_report(self):
        record_data = {
            'class_id': self.class_id.id,
            # 'semister_id': self.semister_id.id,
            'student_id': self.student_id.id,
        }
        return self.env.ref('tvet_management.action_testimonial_continues_preview_report').report_action(self, data=record_data)

    @api.onchange('class_id')
    def class_based_domain(self):
        student_ids = self.env['student.registration'].search([('classroom_id', '=', self.class_id.id), ('status', '=', 'enrolled')])
        domain = [('id', 'in', student_ids.ids)]
        return {'domain': {'student_id': domain}}