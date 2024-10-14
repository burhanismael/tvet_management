# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import calendar


class ResultCourseAssignTemplate(models.AbstractModel):
    _name = 'report.tvet_management.lecturer_assign_report_template'
    _description = 'lecturer assign report template'

    def _get_report_values(self, docids, data=None):
        course_data = {}
        domain = []
        # if data.get('aca_id'):
        #     domain.append(('aca_id', '=', data.get('aca_id')))
        if data.get('lecturer_id'):
            domain.append(('lecturer_name_id.name', '=', data.get('lecturer_id')))
        if data.get('dep_id'):
            domain.append(('school_department_id.name', '=', data.get('dep_id')))
        if data.get('class_id'):
            domain.append(('class_id.name', '=', data.get('class_id')))
        if data.get('sem_id'):
            domain.append(('semester_id.id', 'in', data.get('sem_id')))

        approve_courses = self.env['approve.lecturer'].search(domain)
        lst = []
        for lec in approve_courses:
            print("lecccccccccccccccccccccc", lec.class_id.name)
            for course in  lec.approve_lecturer_line_ids:
                lst.append(course.course_id.name)
        print("lst", lst)

        data = {
            'lecturer_id': data.get('lecturer_id'),
            'approve_courses': approve_courses,

        }
        return data