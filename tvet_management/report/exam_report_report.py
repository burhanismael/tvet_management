# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime



class ExamReportReportTemplate(models.AbstractModel):
    _name = 'report.tvet_management.exam_report_report_template'
    _description = 'Certificate Template'


    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        class_id = False
        acadamic_year_id = False
        semester_id = False
        student_id = False

        class_data = data.get('class_id')
        class_id = self.env['class.room'].browse(class_data)
        previous_class_id = self.env['class.room'].browse(data.get('previous_class_id'))
        total_class = []
        if previous_class_id:
            total_class.append(previous_class_id.id)
        total_class.append(class_id.id)
        acadamic_year = data.get('acadamic_year_id')
        acadamic_year_id = self.env['academic.year'].browse(acadamic_year)
        semister = data.get('semister_id')
        main_class_room_id = self.env['class.room'].search([('name','=',class_id.name)], limit=1)
        main_previous_class_id = self.env['class.room'].search([('name','=',previous_class_id.name)], limit=1)
        semester_id = self.env['semester.semester'].browse(semister)
        student = data.get('student_id')
        if student:
            student_id = self.env['student.registration'].browse(student)
        # # Table Header Data
        class_room_id = main_class_room_id
        main_cource_ids = class_room_id.class_room_ids.filtered(lambda x:x.semester_id.sem_number == semester_id.sem_number).mapped('cource_ids')
        previous_cource_ids = main_previous_class_id.class_room_ids.filtered(lambda x:x.semester_id.sem_number == semester_id.sem_number).mapped('cource_ids')
        course_ids = main_cource_ids
        course_ids |= previous_cource_ids
        data_all = False

        #All Student
        if not student_id:
            data_all = True
            student_ids = self.env['student.registration'].search([('classroom_id', '=', class_id.id), ('status', '=', 'enrolled')])
            cource_exam_ids = self.env['exam.result'].search([('course_name_id', 'in', course_ids.ids), ('class_id', 'in', total_class)])
        else:
            student_ids = self.env['student.registration'].search([('classroom_id', '=', class_id.id), ('status', '=', 'enrolled')])
            cource_exam_ids = self.env['exam.result'].search([('course_name_id', 'in', course_ids.ids), ('class_id', 'in', total_class)])
        data = {
            'docs': docs,
            'course_ids': course_ids,
            'student_ids': student_ids,
            'cource_exam_ids': cource_exam_ids,
            'semester_id': semester_id,
            'data_all': data_all,
            'student_number_id': student_id.student_id if student_id else False,
            'name': student_id.student_name_id.name if student_id else False,
            'student_id': student_id,
            'class_id': class_id.name,
            'semester': semester_id.semester_name
        }
        return data
