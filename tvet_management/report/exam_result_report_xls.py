# -*- coding: utf-8 -*-
from odoo import models, fields
from datetime import datetime
import calendar
from io import BytesIO


class ExamResultReport(models.AbstractModel):
    _name = 'report.tvet_management.exam_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        sheet = workbook.add_worksheet('Attendance_Info')

        format1 = workbook.add_format({'font_size': 10, 'align': 'left' , 'bold': True, 'bg_color': '#D3D3D3'})
        format2 = workbook.add_format({'font_size': 10, 'align': 'left' , 'bold': True})
        format3 = workbook.add_format({'font_size': 15, 'align': 'center', 'bold': True, 'bg_color': '#D3D3D3'})
        format4 = workbook.add_format({'font_size': 10, 'align': 'top', 'bold': True})
        format5 = workbook.add_format({'font_size': 10, 'align': 'center'})

        sheet.insert_image(2, 2, 'tvet_management/static/description/icon.png')
        sheet.insert_image(0, 0, '/opt/odoo15/custom/tvet_management/data/uni_icon.jpeg')
        sheet.merge_range('B5:I5', 'Examination Result Detail', format3)

        row = 7
        col = 0

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

        # top header
        col_show = 2
        if not student_id:
            sheet.write(row, col_show, "All", format2)
        else:
            sheet.write(row, col_show, student_id.student_name_id.name, format2)

        col_show += 1
        sheet.write(row, col_show, "Class Name", format2)
        sheet.set_column(col_show, col_show, 10)
        col_show += 1
        sheet.write(row, col_show, class_id.name, format2)
        row += 1
        col_show = 3
        sheet.write(row, col_show, "Semester", format2)
        sheet.set_column(col_show, col_show, 10)
        col_show += 1
        sheet.write(row, col_show, semester_id.semester_name, format2)

        # Table Header Data
        row += 3
        class_room_id = main_class_room_id
        main_cource_ids = class_room_id.class_room_ids.filtered(lambda x:x.semester_id.sem_number == semester_id.sem_number).mapped('cource_ids')
        previous_cource_ids = main_previous_class_id.class_room_ids.filtered(lambda x:x.semester_id.sem_number == semester_id.sem_number).mapped('cource_ids')
        course_ids = main_cource_ids
        course_ids |= previous_cource_ids

        col = 2
        for cource in course_ids:
            sheet.merge_range(row,col,row,col+1, cource.name, format2)
            sheet.set_column(col, col, 20)
            col += 2

        row += 1
        col = 0
        sheet.write(row, col, "Student ID", format1)
        sheet.set_column(col, col, 20)
        # sheet.set_column(row, col, 20)
        col += 1
        sheet.write(row, col, "Student Name", format1)
        sheet.set_column(col, col, 40)
        col += 1
        for cource in course_ids:
            sheet.write(row, col, "Total", format1)
            col += 1
            sheet.write(row, col, "Grade", format1)
            col += 1
        sheet.write(row, col, "Grade Total", format1)
        sheet.set_column(col, col, 15)
        col += 1
        sheet.write(row, col, "Grade", format1)
        col += 1
        sheet.write(row, col, "GPA", format1)
        col += 1
        row += 1

        #All Student
        if not student_id:
            col = 0
            student_ids = self.env['student.registration'].search([('classroom_id', '=', class_id.id), ('status', '=', 'enrolled')])
            cource_exam_ids = self.env['exam.result'].search([('course_name_id', 'in', course_ids.ids), ('class_id', 'in', total_class)])
            for student in student_ids:
                col = 0
                data_col = 0
                sheet.write(row, col, student.student_id, format2)
                col += 1
                sheet.write(row, col, student.student_name_id.name, format2)
                col += 1
                grade_total = 0
                total_mark_cource = 0
                for cource in course_ids:
                    courcse_wise_exam_ids = cource_exam_ids.filtered(lambda x:x.course_name_id.id == cource.id and x.semester_id.sem_number == semester_id.sem_number)
                    line_ids = courcse_wise_exam_ids.mapped('student_ids').filtered(lambda x:x.student_id.id == student.id)
                    total_mark = sum(line_ids.mapped('marks'))
                    marks = sum(line_ids.mapped('marks'))
                    total_sem_mark = round(marks, 2)
                    grade_total = grade_total + total_mark
                    grade_policy_id = self.env['grading.policy'].search([('minimum', '<=', total_sem_mark),('maximum', '>=', total_sem_mark), ('is_medical', '=', False)], limit=1)
                    sheet.write(row, col, total_mark, format2)
                    col += 1
                    sheet.write(row, col, grade_policy_id.grade, format2)
                    col += 1
                    total_mark_cource = total_mark_cource + total_sem_mark
                    data_col = col
                sheet.write(row, data_col, grade_total, format2)
                data_col += 1
                if total_mark_cource > 0:
                    total_mark_cource_update = total_mark_cource / len(course_ids)
                else:
                    total_mark_cource_update = total_mark_cource
                student_grade_id = self.env['grading.policy'].search([('minimum', '<=', total_mark_cource_update),('maximum', '>=', total_mark_cource_update)], limit=1)
                # sheet.write(row, data_col, student_grade_id.grade, format2)
                data_col += 1
                row += 1
        else:
            col = 0
            data_col = 0
            student_ids = self.env['student.registration'].search([('classroom_id', '=', class_id.id), ('status', '=', 'enrolled')])
            cource_exam_ids = self.env['exam.result'].search([('course_name_id', 'in', course_ids.ids), ('class_id', 'in', total_class)])
            sheet.write(row, col, student_id.student_id, format2)
            col += 1
            sheet.write(row, col, student_id.student_name_id.name, format2)
            col += 1
            grade_total = 0
            total_mark_cource = 0
            for cource in course_ids:
                courcse_wise_exam_ids = cource_exam_ids.filtered(lambda x:x.course_name_id.id == cource.id and x.semester_id.sem_number == semester_id.sem_number)
                total_courcse_count = len(courcse_wise_exam_ids)
                line_ids = courcse_wise_exam_ids.mapped('student_ids').filtered(lambda x:x.student_id.id == student_id.id)
                total_mark = sum(line_ids.mapped('marks'))
                marks = sum(line_ids.mapped('marks'))
                total_sem_mark = round(marks, 2)
                grade_total = grade_total + total_mark
                grade_policy_id = self.env['grading.policy'].search([('minimum', '<=', total_sem_mark),('maximum', '>=', total_sem_mark)], limit=1)
                sheet.write(row, col, total_mark, format2)
                col += 1
                sheet.write(row, col, grade_policy_id.grade, format2)
                col += 1
                total_mark_cource = total_mark_cource + total_sem_mark
                data_col = col
            sheet.write(row, data_col, grade_total, format2)
            data_col += 1
            if total_mark_cource > 0:
                total_mark_cource_update = total_mark_cource / len(course_ids)
            else:
                total_mark_cource_update = total_mark_cource
            student_grade_id = self.env['grading.policy'].search([('minimum', '<=', total_mark_cource_update),('maximum', '>=', total_mark_cource_update)], limit=1)
            # sheet.write(row, data_col, student_grade_id.grade, format2)
            data_col += 1
            row += 1
