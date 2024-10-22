# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import calendar

class ResultTimeTableTemplate(models.AbstractModel):
    _name = 'report.tvet_management.report_time_table_report_id'
    _description = 'Report  Result Transcriprt Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        class_id = self.env['class.room'].browse(data.get('class_id'))
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        semester_id = data.get('semester_id')

        domain = []

        if data.get('date_from'):
            domain.append(('time_table_date', '>=', data.get('date_from')))

        if data.get('date_to'):
            domain.append(('time_table_date', '<=', data.get('date_to')))
        if data.get('class_id'):
            domain.append(('class_id', '=', data.get('class_id')))
        if data.get('semister_id'):
            domain.append(('semester_id', '=', data.get('semister_id')))

        course_ids = self.env['manage.timetable'].search(domain)
        print("cccccccccc", course_ids)

        data = {
            'doc_ids': docids,
            'doc_model': 'time.table.wizard',
            'data': data,
            'date_from': data.get('date_from'),
            'date_to': data.get('date_to'),
            'course_ids': course_ids,
        }
        return data