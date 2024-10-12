# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import calendar


class ResultCourseAssignTemplate(models.AbstractModel):
    _name = 'report.tvet_management.course_assign_template'
    _description = 'Report  course assign template'

    def _get_report_values(self, docids, data=None):
        course_data = {}
        domain = []

        if data.get('department_id'):
            domain.append(('school_department_id.name', '=', data.get('department_id')))
        if data.get('class_id'):
            domain.append(('class_id.name', '=', data.get('class_id')))
        if data.get('semister_id'):
            domain.append(('semester_name_id.semester_name', '=', data.get('semister_id')))
        if data.get('aca_id'):
            domain.append(('aca_id', '=', data.get('aca_id')))
        domain.append(('status', '=', 'approved'))

        course_ids = self.env['approve.course'].search(domain)

        for rec in course_ids:
            class_name = rec.class_id.name
            semester_name = rec.semester_name_id.semester_name
            semester_no = rec.semester_name_id.sem_number
            if semester_no not in course_data:
                course_data[semester_no] = {'class': class_name,'name': semester_name, 'courses': []}
            course_data[semester_no]['courses'].extend(
                [course.name for course_id in rec.course_approve_line_ids for course in course_id.course]
            )

        # Sort course_data by semester_no
        sorted_course_data = dict(sorted(course_data.items()))

        data.update({
            'sorted_course_data': sorted_course_data  # Include sorted courses data here
        })

        return {
            'doc_ids': docids,
            'doc_model': 'approve.course',
            'data': data,
        }
