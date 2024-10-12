# -*- coding: utf-8 -*-
from odoo import models, fields
from datetime import datetime
import calendar
from io import BytesIO


class ExamSummaryReport(models.AbstractModel):
    _name = 'report.tvet_management.exam_result_summary'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        sheet = workbook.add_worksheet('Attendance_Info')

        format1 = workbook.add_format({'font_size': 10, 'align': 'left' , 'bold': True, 'bg_color': '#D3D3D3'})
        format2 = workbook.add_format({'font_size': 10, 'align': 'left' , 'bold': True})
        format3 = workbook.add_format({'font_size': 15, 'align': 'center', 'bold': True, 'bg_color': '#D3D3D3'})
        format4 = workbook.add_format({'font_size': 10, 'align': 'top', 'bold': True})
        format5 = workbook.add_format({'font_size': 10, 'align': 'center'})

        # sheet.insert_image(2, 2, 'tvet_management/static/description/icon.png')
        sheet.insert_image(0, 0, '/opt/odoo15/custom/tvet_management/data/uni_icon.jpeg')
        sheet.merge_range('B5:H5', 'Exam Result Summary', format3)

        row = 7
        col = 0

        class_id = False
        acadamic_year_id = False
        semester_id = False
        student_id = False

        class_data = data.get('class_id')
        class_id = self.env['class.room'].browse(class_data)
        previous_class_id = self.env['class.room'].browse(data.get('previous_class_id'))
        acadamic_year = data.get('acadamic_year_id')
        acadamic_year_id = self.env['academic.year'].browse(acadamic_year)
        semister = data.get('semister_id')
        main_class_room_id = self.env['class.room'].search(
            [('name', '=', class_id.name)], limit=1)
        previous_class_room_id = self.env['class.room'].search(
            [('name', '=', previous_class_id.name)], limit=1)
        total_class = []
        if previous_class_room_id:
            total_class.append(previous_class_room_id.id)
        total_class.append(class_id.id)
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
        # col_show = 3
        # sheet.write(row, col_show, "Semester", format2)
        # col_show += 1
        # sheet.write(row, col_show, semester_id.semester_name, format2)

        # Table Header Data
        row += 3
        class_room_id = main_class_room_id
        main_class_cource_ids = class_room_id.class_room_ids.filtered(lambda x:x.semester_id.sem_number == semester_id.sem_number).mapped('cource_ids')
        previous_cource_ids = previous_class_room_id.class_room_ids.filtered(lambda x:x.semester_id.sem_number == semester_id.sem_number).mapped('cource_ids')
        course_ids = main_class_cource_ids
        course_ids |= previous_cource_ids
        col = 2
        # for cource in course_ids:
        #     sheet.write(row,col, cource.course_name, format2)
        #     col += 1
        #     print(col)
        row += 1
        col = 0
        sheet.write(row, col, "Student ID", format1)
        sheet.set_column(col, col, 20)
        col += 1
        sheet.write(row, col, "Student Name", format1)
        sheet.set_column(col, col, 40)
        col += 1
        for cource in course_ids:
            sheet.write(row, col, cource.name, format1)
            sheet.set_column(col, col, 20)
            col += 1
        sheet.write(row, col, "Total", format1)
        col += 1
        sheet.write(row, col, "Average", format1)
        col += 1
        sheet.write(row, col, "Grade", format1)
        col += 1
        sheet.write(row, col, "Re-Exam Course", format1)
        sheet.set_column(col, col, 20)
        col += 1
        row += 1

        #All Student
        if not student_id:
            col = 0
            student_ids = self.env['student.registration'].search([('classroom_id', '=', class_id.id), ('status', '=', 'enrolled')])
            cource_exam_ids = self.env['exam.result'].search([('course_name_id', 'in', course_ids.ids), ('class_id', 'in', total_class)])
            for student in student_ids:
                reexamcource = []
                col = 0
                sheet.write(row, col, student.student_id, format2)
                col += 1
                sheet.write(row, col, student.student_name_id.name, format2)
                col += 1
                for cource in course_ids:
                    line_ids = cource_exam_ids.filtered(lambda x:x.course_name_id.id == cource.id and x.semester_id.sem_number == semester_id.sem_number).mapped('student_ids').filtered(lambda x:x.student_id.id == student.id)
                    total_mark = sum(line_ids.mapped('marks'))
                    sheet.write(row, col, total_mark, format2)
                    col += 1
                    is_medical = cource.is_medical
                    grade_policy_id = self.env['grading.policy'].search([('minimum', '<=', total_mark),('maximum', '>=', total_mark), ('is_medical', '=', is_medical)], limit=1)
                    if grade_policy_id.grade == 'F':
                        reexamcource.append(cource.name)
                reexamdetails = ",".join(reexamcource)
                total_cource_mark = cource_exam_ids.filtered(lambda x:x.semester_id.sem_number == semester_id.sem_number).mapped('student_ids').filtered(lambda x:x.student_id.id == student.id)
                total_mark_cource = sum(total_cource_mark.mapped('marks'))
                sheet.write(row, col, total_mark_cource, format2)
                col += 1
                total_courcse = len(course_ids)
                # avarge = (total_mark_cource/(total_courcse*100))*100
                # sheet.write(row, col, avarge, format2)
                col += 1
                sheet.write(row, col, 0, format2)
                col += 1
                for reexam in reexamcource:
                    sheet.write(row, col, reexam, format2)
                    row += 1
        else:
            col = 0
            student_ids = self.env['student.registration'].search([('classroom_id', '=', class_id.id), ('status', '=', 'enrolled')])
            cource_exam_ids = self.env['exam.result'].search([('course_name_id', 'in', course_ids.ids), ('class_id', 'in', total_class)])
            sheet.write(row, col, student_id.student_id, format2)
            col += 1
            sheet.write(row, col, student_id.student_name_id.name, format2)
            col += 1
            reexamcource = []
            for cource in course_ids:
                line_ids = cource_exam_ids.filtered(lambda x:x.course_name_id.id == cource.id and x.semester_id.sem_number == semester_id.sem_number).mapped('student_ids').filtered(lambda x:x.student_id.id == student_id.id)
                total_mark = sum(line_ids.mapped('marks'))
                sheet.write(row, col, total_mark, format2)
                col += 1
                is_medical = cource.is_medical
                grade_policy_id = self.env['grading.policy'].search([('minimum', '<=', total_mark),('maximum', '>=', total_mark), ('is_medical', '=', is_medical)], limit=1)
                if grade_policy_id.grade == 'F':
                    reexamcource.append(cource.name)
            total_cource_mark = cource_exam_ids.filtered(lambda x:x.semester_id.sem_number == semester_id.sem_number).mapped('student_ids').filtered(lambda x:x.student_id.id == student_id.id)
            total_mark_cource = sum(total_cource_mark.mapped('marks'))
            sheet.write(row, col, total_mark_cource, format2)
            col += 1
            total_courcse = len(course_ids)
            avarge = (total_mark_cource/(total_courcse*100))*100
            sheet.write(row, col, avarge, format2)
            col += 1
            sheet.write(row, col, 0, format2)
            col += 1
            for reexam in reexamcource:
                sheet.write(row, col, reexam, format2)
                row += 1
