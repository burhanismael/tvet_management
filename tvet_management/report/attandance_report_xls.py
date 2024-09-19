# -*- coding: utf-8 -*-
from odoo import models, fields
from datetime import datetime
import calendar
from io import BytesIO


class AttendanceReport(models.AbstractModel):
    _name = 'report.tvet_management.attendanace_data_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        sheet = workbook.add_worksheet('Attendance_Info')

        format1 = workbook.add_format({'font_size': 10, 'align': 'left' , 'bold': True, 'bg_color': '#D3D3D3'})
        format2 = workbook.add_format({'font_size': 10, 'align': 'left' , 'bold': True})
        format3 = workbook.add_format({'font_size': 10, 'align': 'center'})
        format4 = workbook.add_format({'font_size': 10, 'align': 'top', 'bold': True})

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

        # sheet.insert_image(2, 2, 'tvet_management/static/description/icon.png')
        sheet.insert_image(0, 0, '/opt/odoo15/custom/tvet_management/data/uni_icon.jpeg')

        row = 6
        col = 0
        sheet.write(row, col, "Date From :", format1)
        sheet.set_column(col, col, 20)
        col += 1
        date_display = datetime.strptime(str(date), "%Y-%m-%d").strftime('%d-%b,%Y')
        sheet.write(row, col, date_display, format2)
        sheet.set_column(col, col, 20)
        col += 1
        sheet.write(row, col, "Date To :", format1)
        sheet.set_column(col, col, 20)
        col += 1
        date_display_to = datetime.strptime(str(date_to), "%Y-%m-%d").strftime('%d-%b,%Y')
        sheet.write(row, col, date_display_to, format2)
        sheet.set_column(col, col, 20)
        col += 1
        sheet.write(row, col, "DEPARTMENT NAME:", format1)
        sheet.set_column(col, col, 20)
        col += 1
        if department_id:
            sheet.write(row, col, department_id.name , format2)
            sheet.set_column(col, col, 20)
            col += 1
        else:
            sheet.write(row, col, '' , format2)
            col += 1
        sheet.write(row, col, "CLASS NAME:", format1)
        sheet.set_column(col, col, 20)
        col += 1
        sheet.write(row, col, class_id.name , format2)
        sheet.set_column(col, col, 20)
        col += 1
        sheet.write(row, col, "SEMESTER:", format1)
        sheet.set_column(col, col, 20)
        col += 1
        sheet.write(row, col, sem_id.semester_name , format2)
        sheet.set_column(col, col, 20)
        row += 2
        col_data = 0
        sheet.write(row, col_data, "Course Name", format1)
        sheet.set_column(col_data, col_data, 20)
        col_data += 1
        sheet.write(row, col_data, "#", format1)
        col_data += 1
        sheet.write(row, col_data, "Student ID", format1)
        sheet.set_column(col_data, col_data, 20)
        col_data += 1
        sheet.write(row, col_data, "Student Name", format1)
        sheet.set_column(col_data, col_data, 40)
        col_data += 1
        sheet.write(row, col_data, "Present SESIONS", format1)
        col_data += 1
        sheet.write(row, col_data, "Absent SESIONS", format1)
        col_data += 1
        sheet.write(row, col_data, "NOT TAKEN", format1)
        col_data += 1
        sheet.write(row, col_data, "TOTAL SESIONS", format1)
        col_data += 1
        sheet.write(row, col_data, "Level of Attendance", format1)
        col_data += 1
        sheet.write(row, col_data, "Status", format1)
        col_data += 1
        row += 1

        attendance_company = self.env.company.at_dance
        if cource_id:
            all_related_data = self.env['attendance.sheet'].search([('date', '>=', date), ('date', '<=', date_to), ('class_id', '=', class_id.id), ('semester_id', '=', sem_id.id), ('course_name_id', 'in', cource_id.ids)])
        else:
            all_related_data = self.env['attendance.sheet'].search([('date', '>=', date), ('date', '<=', date_to), ('class_id', '=', class_id.id), ('semester_id', '=', sem_id.id)])
        cource_ids = all_related_data.mapped('course_name_id')
        for cource in cource_ids:
            col_data_at = 0 
            index = 1
            cource_session_ids = all_related_data.filtered(lambda x:x.course_name_id.id == cource.id and x.student_ids and len(x.student_ids.mapped('student_id')) > 0)
            student_data = len(cource_session_ids.mapped('student_ids').mapped('student_id'))
            total_session = len(cource_session_ids.ids)
            if total_session > 0:
                student_ids = self.env['student.registration'].search([('classroom_id', '=', class_id.id), ('status', '=', 'enrolled')])
                total_student = len(student_ids)
                row_add = total_student - 1
                sheet.merge_range(row, col_data_at, row+row_add, col_data_at, cource.course_name, format4)
                col_data_at += 1
                for attendance in student_ids:
                    col_data_at = 1
                    sheet.write(row, col_data_at, index, format2)
                    index += 1
                    col_data_at += 1
                    sheet.write(row, col_data_at, attendance.student_id, format2)
                    col_data_at += 1
                    sheet.write(row, col_data_at, attendance.student_name_id.name, format2)
                    col_data_at += 1
                    student_data = cource_session_ids.mapped('student_ids').filtered(lambda x:x.student_id.id == attendance.id)
                    present_data = len(student_data.filtered(lambda x:x.checkbox))
                    sheet.write(row, col_data_at, present_data, format2)
                    col_data_at += 1
                    abesent_data = len(student_data.filtered(lambda x:x.checkbox2))
                    sheet.write(row, col_data_at, abesent_data, format2)
                    col_data_at += 1
                    abesent_data_not_select = total_session - (present_data + abesent_data)
                    sheet.write(row, col_data_at, abesent_data_not_select, format2)
                    col_data_at += 1
                    sheet.write(row, col_data_at, total_session, format2)
                    col_data_at += 1
                    present_level = 0
                    if present_data > 0 : 
                        present_level_data = ((present_data + abesent_data_not_select) / total_session) * 100
                        present_level = round(present_level_data, 2)
                    sheet.write(row, col_data_at, present_level, format2)
                    col_data_at += 1
                    result_attandance = "Fail"
                    if int(attendance_company) <= int(present_level):
                        result_attandance = "Pass"
                    sheet.write(row, col_data_at, result_attandance, format2)
                    col_data_at += 1
                    row += 1
