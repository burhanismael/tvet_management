# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import calendar

class TestimonialGraduationReportTemplate(models.AbstractModel):
    _name = 'report.tvet_management.testimonial_graduation_report_template'
    _description = 'Testimonial Graduation Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        data = {
            'student_id': docs.student_id,
        }
        return data
