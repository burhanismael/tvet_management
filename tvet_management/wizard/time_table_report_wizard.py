# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class TestimonialGraduationWizard(models.TransientModel):
    _name = "time.table.wizard"
    _description = 'time.table.wizard'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    class_id = fields.Many2one('class.room', string="Class")
    semester_id = fields.Many2one('semester.semester', string="Semester")

    def pdf_report(self):
        record_data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'class_id': self.class_id.id,
            'semester_id': self.semester_id.id,
        }
        return self.env.ref('tvet_management.action_time_table_report_template').report_action(self, data=record_data)