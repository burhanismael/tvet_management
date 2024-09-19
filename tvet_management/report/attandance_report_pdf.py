# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
import calendar
from io import BytesIO


class AttendanceReportPdf(models.AbstractModel):
    _name = 'report.tvet_management.attandance_report_template'
    _description = 'Attandance Template'


    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        date = data.get('date')
        date_to = data.get('date_to')

        department_id = False
        class_id = False
        sem_id = False
        cource_id = False

        if data.get('school_department_id'):
            department_id = self.env['school.department'].browse(data.get('school_department_id'))
        if data.get('class_id'):
            class_id = self.env['class.room'].browse(data.get('class_id'))
        if data.get('semester_id'):
            sem_id = self.env['semester.semester'].browse(data.get('semester_id'))
        if data.get('cource_ids'):
            cource_id = self.env['course.subject'].browse(data.get('cource_ids'))

        attendance_company = self.env.company.at_dance
        if cource_id:
            all_related_data = self.env['attendance.sheet'].search([('date', '>=', date), ('date', '<=', date_to), ('class_id', '=', class_id.id), ('semester_id', '=', sem_id.id), ('course_name_id', 'in', cource_id.ids)])
        else:
            all_related_data = self.env['attendance.sheet'].search([('date', '>=', date), ('date', '<=', date_to), ('class_id', '=', class_id.id), ('semester_id', '=', sem_id.id)])
        cource_ids = all_related_data.mapped('course_name_id')

        return {
            'docs': docs,
            'department_id': department_id,
            'class_id': class_id,
            'sem_id': sem_id,
            'date': date,
            'date_to': date_to,
            'cource_ids': cource_ids,
            'all_related_data': all_related_data
        }
