import json
from odoo import fields, http, SUPERUSER_ID, _
from odoo.addons.portal.controllers import portal
from odoo import http
from odoo.http import content_disposition, request
from werkzeug.exceptions import BadRequest
import base64
import ast

class CustomerPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        employee_id = request.env.user.employee_id
        partner_id = request.env.user.partner_id
        student_id = request.env['student.registration'].sudo().search([('student_name_id', '=', partner_id.id)], limit=1)
        if 'result_count' in counters:
            result_id = request.env['exam.result.entry.line']
            result_ids = result_id.sudo().search([('student_id', '=', student_id.id), ('exam_result_entry_id.status', '=', 'ar_approved')])
            entry_ids = result_ids.mapped('exam_result_entry_id')
            semester_ids = entry_ids.mapped('semester_id')
            cource_ids = entry_ids.mapped('course_name_id')
            values['result_count'] = len(semester_ids)
        if 'attendance_count' in counters:
            attendance_id = request.env['attendance.sheet.line']
            attendance_ids = attendance_id.sudo().search([('student_id', '=', student_id.id)])
            values['attendance_count'] = len(attendance_ids)
        if 'time_table_count' in counters:
            timetable_id = request.env['manage.timetable']
            time_table_ids = timetable_id.sudo().search([('school_department_id', '=', student_id.department_id.id), ('class_id', '=', student_id.classroom_id.id), ('semester_id', '=', student_id.semester_id.id)])
            values['time_table_count'] = len(time_table_ids)
        return values

    @http.route(['/my/results', '/my/results/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_projects(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        result_id = request.env['exam.result.entry.line']
        partner_id = request.env.user.partner_id
        # settings_record = request.env['res.config.settings'].sudo().search([], order="id desc", limit=1)
        # examination_boolean_value = settings_record.examination_boolean
        # if examination_boolean_value == True:
        if partner_id.credit > 0:
            values['credit_error'] = True  # Set the flag for the popup
            return request.render("tvet_management.exam_result_details_error", values)

        student_id = request.env['student.registration'].sudo().search([('student_id', '=', partner_id.email)], limit=1)
        type_data_ids = request.env['exam.type'].sudo().search([('is_portal', '=', True)])
        result_ids = result_id.sudo().search([('student_id', '=', student_id.id), ('exam_result_entry_id.status', '=', 'ar_approved')])
        approval_exam_ids = []
        for exam_type in type_data_ids:
            mark = sum(result_ids.filtered(lambda x:x.exam_result_entry_id.exam_type_id.id == exam_type.id).mapped('marks'))
            if mark > 0 :
                approval_exam_ids.append(exam_type.id)
        entry_ids = result_ids.mapped('exam_result_entry_id')
        cource_ids = entry_ids.mapped('course_name_id')
        data_record = []
        type_ids = request.env['exam.type']
        if len(approval_exam_ids) > 0:
            type_ids = request.env['exam.type'].sudo().browse(approval_exam_ids)
        main_semester_ids = []
        for cource in cource_ids:
            data_ids = result_ids.filtered(lambda x:x.exam_result_entry_id.course_name_id.id == cource.id)
            if data_ids:
                exam_result_entry_ids = data_ids.mapped('exam_result_entry_id')
                semister_ids = exam_result_entry_ids.mapped('semester_id')
                if semister_ids:
                    main_semester_ids.extend(semister_ids.ids)
                for sem in semister_ids:
                    data_dict = {}
                    data_dict['date'] = data_ids[0].exam_result_entry_id.date
                    data_dict['cource'] = cource.name
                    data_dict['semester'] = sem.semester_name
                    data_dict['class'] = data_ids[0].exam_result_entry_id.class_id.name
                    result = []
                    total = 0
                    gpa = 0
                    for exam_type in type_ids:
                        mark = sum(data_ids.filtered(lambda x:x.exam_result_entry_id.exam_type_id.id == exam_type.id and x.exam_result_entry_id.semester_id.id == sem.id).mapped('marks'))
                        result.append(mark)
                        data_dict['result'] = result
                        total = sum(result)
                    data_dict['total'] = total
                    data_record.append(data_dict)
        total_sem_ids = request.env['semester.semester'].browse(list(set(main_semester_ids)))
        values.update({
            'page_name': 'exam_result',
            'result_ids': result_ids,
            'type_ids': type_ids,
            'data_ids': data_record,
            'semister_ids': total_sem_ids
        })
        return request.render("tvet_management.exam_result_details", values)

    @http.route([
        '/semester_details/<int:semester_id>',
    ], type='http', auth="public", website=True)
    def semester_details_view(self, semester_id=None, access_token=None, **kw):
        values = self._prepare_portal_layout_values()
        result_id = request.env['exam.result.entry.line']
        partner_id = request.env.user.partner_id
        student_id = request.env['student.registration'].sudo().search([('student_id', '=', partner_id.email)], limit=1)
        type_data_ids = request.env['exam.type'].sudo().search([('is_portal', '=', True)])
        result_ids = result_id.sudo().search([('student_id', '=', student_id.id), ('exam_result_entry_id.status', '=', 'ar_approved')])
        grading_policy_ids = request.env['grading.policy'].sudo().search([])
        is_medical_ids = grading_policy_ids.filtered(lambda x: x.is_medical)
        grading_ids = grading_policy_ids.filtered(lambda x: not x.is_medical)
        approval_exam_ids = []
        total_gpa = []
        course_list = []
        average_gpa = 0.0
        for exam_type in type_data_ids:
            mark = sum(result_ids.filtered(lambda x:x.exam_result_entry_id.exam_type_id.id == exam_type.id).mapped('marks'))
            if mark > 0 :
                approval_exam_ids.append(exam_type.id)
        entry_ids = result_ids.mapped('exam_result_entry_id')
        cource_ids = entry_ids.mapped('course_name_id')
        data_record = []
        type_ids = request.env['exam.type']
        if len(approval_exam_ids) > 0:
            type_ids = request.env['exam.type'].sudo().browse(approval_exam_ids)
        for cource in cource_ids:
            data_ids = result_ids.filtered(lambda x:x.exam_result_entry_id.course_name_id.id == cource.id)

            if data_ids:
                exam_result_entry_ids = data_ids.mapped('exam_result_entry_id')
                semister_ids = exam_result_entry_ids.filtered(lambda x:x.semester_id.id == semester_id).mapped('semester_id')

                for sem in semister_ids:
                    data_dict = {}
                    data_dict['date'] = data_ids[0].exam_result_entry_id.date
                    data_dict['cource'] = cource.name
                    data_dict['semester'] = sem.semester_name
                    data_dict['class'] = data_ids[0].exam_result_entry_id.class_id.name
                    result = []
                    total = 0
                    for exam_type in type_ids:
                        mark = sum(data_ids.filtered(lambda x:x.exam_result_entry_id.exam_type_id.id == exam_type.id and x.exam_result_entry_id.semester_id.id == sem.id).mapped('marks'))
                        result.append(mark)
                        data_dict['result'] = result
                        total = sum(result)
                    data_dict['total'] = total
                    if cource.is_medical == False:
                        student_grading_ids = grading_ids.filtered(lambda x: x.minimum <= total and x.maximum >= total)
                        if student_grading_ids:
                            gpa = float(student_grading_ids[0].gpa)
                            grade = student_grading_ids[0].grade
                        else:
                            gpa = 0.0
                            grade = "F"
                    else:
                        student_grading_ids = is_medical_ids.filtered(lambda x: x.minimum <= total and x.maximum >= total)
                        if student_grading_ids:
                            gpa = float(student_grading_ids[0].gpa)
                            grade = student_grading_ids[0].grade
                        else:
                            gpa = 0.0
                            grade = "F"
                    total_gpa.append(gpa)
                    course_list.append(cource)
                    average_gpa = round(sum(total_gpa) / len(course_list), 2)


                    data_dict['gpa'] = gpa
                    data_dict['grade'] = grade
                    data_dict['average_gpa'] = average_gpa
                    data_record.append(data_dict)
        values.update({
            'page_name': 'exam_result',
            'result_ids': result_ids,
            'type_ids': type_ids,
            'data_ids': data_record,
        })
        return request.render("tvet_management.portal_my_result", values)

    @http.route(['/my/attendance', '/my/attendance/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_attandance(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        attendance_id = request.env['attendance.sheet.line']
        partner_id = request.env.user.partner_id
        student_id = request.env['student.registration'].sudo().search([('student_id', '=', partner_id.email)], limit=1)
        attendance_ids = attendance_id.sudo().search([('student_id', '=', student_id.id)])
        values.update({
            'page_name': 'attendance',
            'attendance_ids': attendance_ids
        })
        return request.render("tvet_management.portal_my_attandance", values)

    @http.route(['/my/timetable', '/my/timetable/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_timetable(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        timetable_id = request.env['manage.timetable']
        partner_id = request.env.user.partner_id
        student_id = request.env['student.registration'].sudo().search([('student_id', '=', partner_id.email)], limit=1)
        time_table_ids = timetable_id.sudo().search([('school_department_id', '=', student_id.department_id.id), ('class_id', '=', student_id.classroom_id.id), ('semester_id', '=', student_id.semester_id.id)])
        values.update({
            'page_name': 'timetable',
            'time_table_ids': time_table_ids
        })
        return request.render("tvet_management.portal_my_timetable", values)

    @http.route(['/my/material', '/my/material/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_learning_materials(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        timetable_id = request.env['learning.material']
        partner_id = request.env.user.partner_id
        student_id = request.env['student.registration'].sudo().search([('student_id', '=', partner_id.email)], limit=1)
        learning_material_ids = timetable_id.sudo().search(
            [('department_id', '=', student_id.department_id.id)])
        print("sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss", learning_material_ids)
        # for result in learning_material_ids:
        #     if isinstance(result.attechment, bytes):
        #         attachment = request.env['ir.attachment'].sudo().create({
        #             'name': 'filename.pdf',  # Set an appropriate file name
        #             'type': 'binary',
        #             'datas': base64.b64encode(result.attechment),  # Encoding the binary data
        #             'res_model': 'learning.material',
        #             'res_id': result.id,
        #         })
        #         result.sudo().attechment = attachment.id  # Set the Many2one field
        #     else:
        #         raise TypeError("The attachment data is not in binary format.")

        values.update({
            'page_name': 'learningmaterial',
            'learning_material_ids': learning_material_ids
        })
        return request.render("tvet_management.portal_my_timetable", values)


    @http.route(['/examination/view/<int:class_id>/<int:aca_id>/<int:semister_id>/', '/examination/view/page/<int:page>'], type='http', auth="user", website=True)
    def portal_examination_view(self, class_id, aca_id, semister_id, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        class_id = request.env['class.room'].sudo().browse(class_id)
        aca_id = request.env['academic.year'].sudo().browse(aca_id)
        semister_id = request.env['semester.semester'].sudo().browse(semister_id)
        result_ids = request.env['exam.result'].sudo().search([('class_id', '=', class_id.id), ('academic_year_id', '=', aca_id.id), ('semester_id', '=', semister_id.id)])
        exam_type_ids = result_ids.mapped('exam_type_id')
        course_name_ids = result_ids.mapped('course_name_id')
        student_data = []
        student_ids = request.env['student.registration'].search([('classroom_id', '=', class_id.id)])
        for student in student_ids:
            student_dict = {'student_id': student.id, 'admission_id': student.student_id, 'student_name': student.student_name_id.name}
            cource_dict = []
            all_line_not_available = []
            for cource in course_name_ids:

                exam_type_dict = []
                exam_type_ids_data = result_ids.filtered(lambda x:x.course_name_id.id == cource.id and x.status in ['dean_approval', 'approved', 'ar_approved']).mapped('exam_type_id')
                for exam_type in exam_type_ids_data:
                    exam_type_id = result_ids.filtered(lambda x:x.exam_type_id.id == exam_type.id and x.course_name_id.id == cource.id and x.status in ['dean_approval', 'approved', 'ar_approved'])
                    if exam_type_id:
                        exam_line_id = exam_type_id[0].mapped('student_ids').filtered(lambda x:x.student_id.id == student.id)
                        if exam_line_id:
                            all_line_not_available.append(True)
                        else:
                            all_line_not_available.append(False)
                        exam_type_dict.append({'exam_type':exam_type.id, 'exam_line_id':exam_line_id})
                    else:
                        exam_line_id = False
                        all_line_not_available.append(False)
                cource_dict.append({'exam_records': exam_type_dict})
            student_dict.update({'cource_records': cource_dict})
            if any(all_line_not_available):
                student_data.append(student_dict)

        values = {
            'class_id': class_id.id,
            'aca_id': aca_id.id,
            'semister_id': semister_id.id,
            'student_data': student_data,
            'result_ids': result_ids,
            'course_name_ids': course_name_ids,
            'exam_type_ids': exam_type_ids,
            'total_exam_type': str(len(exam_type_ids) + 1)
        }
        return request.render("tvet_management.examination_result", values)
    @http.route(['/examination/view/<int:class_id>/<int:aca_id>/<int:semister_id>/<int:student_id>/<int:cource_id>/', '/examination/view/page/<int:page>'], type='http', auth="user", website=True)
    def portal_examination_view_class_courses(self, class_id, aca_id, semister_id, student_id,cource_id, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        if student_id == 482:
            self.portal_examination_view_classes(self, class_id, aca_id, semister_id, cource_id, page=1, date_begin=None, date_end=None, sortby=None, **kw)
        else:
            class_id = request.env['class.room'].sudo().browse(class_id)
            aca_id = request.env['academic.year'].sudo().browse(aca_id)
            semister_id = request.env['semester.semester'].sudo().browse(semister_id)
            student_id = request.env['student.registration'].sudo().browse(student_id)
            result_ids = request.env['exam.result'].sudo().search([('class_id', '=', class_id.id), ('academic_year_id', '=', aca_id.id), ('semester_id', '=', semister_id.id)])
            exam_type_ids = result_ids.mapped('exam_type_id')
            course_name_ids = result_ids.mapped('course_name_id')
            student_data = []
            student_ids = student_id
            for student in student_ids:
                student_dict = {'student_id': student.id, 'admission_id': student.student_id, 'student_name': student.student_name_id.name}
                cource_dict = []
                all_line_not_available = []
                for cource in course_name_ids:

                    exam_type_dict = []
                    exam_type_ids_data = result_ids.filtered(lambda x:x.course_name_id.id == cource.id and x.status in ['dean_approval', 'approved', 'ar_approved']).mapped('exam_type_id')
                    for exam_type in exam_type_ids_data:
                        exam_type_id = result_ids.filtered(lambda x:x.exam_type_id.id == exam_type.id and x.course_name_id.id == cource.id and x.status in ['dean_approval', 'approved', 'ar_approved'])
                        if exam_type_id:
                            exam_line_id = exam_type_id[0].mapped('student_ids').filtered(lambda x:x.student_id.id == student.id)
                            if exam_line_id:
                                all_line_not_available.append(True)
                            else:
                                all_line_not_available.append(False)
                            exam_type_dict.append({'exam_type':exam_type.id, 'exam_line_id':exam_line_id})
                        else:
                            exam_line_id = False
                            all_line_not_available.append(False)
                    cource_dict.append({'exam_records': exam_type_dict})
                student_dict.update({'cource_records': cource_dict})
                if any(all_line_not_available):
                    student_data.append(student_dict)

            values = {
                'class_id': class_id.id,
                'aca_id': aca_id.id,
                'semister_id': semister_id.id,
                'student_data': student_data,
                'result_ids': result_ids,
                'course_name_ids': course_name_ids,
                'exam_type_ids': exam_type_ids,
                'total_exam_type': str(len(exam_type_ids) + 1)
            }
            return request.render("tvet_management.examination_result", values)

    @http.route(['/examination/view/<int:class_id>/<int:aca_id>/<int:semister_id>/<int:cource_id>/', '/examination/view/page/<int:page>'], type='http', auth="user", website=True)
    def portal_examination_view_classes(self, class_id, aca_id, semister_id, cource_id, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        class_id = request.env['class.room'].sudo().browse(class_id)
        aca_id = request.env['academic.year'].sudo().browse(aca_id)
        semister_id = request.env['semester.semester'].sudo().browse(semister_id)
        cource_id = request.env['course.subject'].sudo().browse(cource_id)
        result_ids = request.env['exam.result'].sudo().search([('class_id', '=', class_id.id), ('academic_year_id', '=', aca_id.id), ('semester_id', '=', semister_id.id)])
        exam_type_ids = result_ids.mapped('exam_type_id')
        course_name_ids = cource_id
        student_data = []
        student_ids = request.env['student.registration'].search([('classroom_id', '=', class_id.id)])
        for student in student_ids:
            student_dict = {'student_id': student.id, 'admission_id': student.student_id, 'student_name': student.student_name_id.name}
            cource_dict = []
            all_line_not_available = []
            for cource in course_name_ids:

                exam_type_dict = []
                exam_type_ids_data = result_ids.filtered(lambda x:x.course_name_id.id == cource.id and x.status in ['dean_approval', 'approved', 'ar_approved']).mapped('exam_type_id')
                for exam_type in exam_type_ids_data:
                    exam_type_id = result_ids.filtered(lambda x:x.exam_type_id.id == exam_type.id and x.course_name_id.id == cource.id and x.status in ['dean_approval', 'approved', 'ar_approved'])
                    if exam_type_id:
                        exam_line_id = exam_type_id[0].mapped('student_ids').filtered(lambda x:x.student_id.id == student.id)
                        if exam_line_id:
                            all_line_not_available.append(True)
                        else:
                            all_line_not_available.append(False)
                        exam_type_dict.append({'exam_type':exam_type.id, 'exam_line_id':exam_line_id})
                    else:
                        exam_line_id = False
                        all_line_not_available.append(False)
                cource_dict.append({'exam_records': exam_type_dict})
            student_dict.update({'cource_records': cource_dict})
            if any(all_line_not_available):
                student_data.append(student_dict)

        values = {
            'class_id': class_id.id,
            'aca_id': aca_id.id,
            'semister_id': semister_id.id,
            'student_data': student_data,
            'result_ids': result_ids,
            'course_name_ids': course_name_ids,
            'exam_type_ids': exam_type_ids,
            'total_exam_type': str(len(exam_type_ids) + 1)
        }
        return request.render("tvet_management.examination_result", values)


    @http.route(['/examination/view/<int:class_id>/<int:aca_id>/<int:semister_id>/<int:cource_id>/<int:student_id>/', '/examination/view/page/<int:page>'], type='http', auth="user", website=True)
    def portal_examination_view_class_adn_student(self, class_id, aca_id, semister_id, cource_id, student_id, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        class_id = request.env['class.room'].sudo().browse(class_id)
        aca_id = request.env['academic.year'].sudo().browse(aca_id)
        semister_id = request.env['semester.semester'].sudo().browse(semister_id)
        student_id = request.env['student.registration'].sudo().browse(student_id)
        cource_id = request.env['course.subject'].sudo().browse(cource_id)
        result_ids = request.env['exam.result'].sudo().search([('class_id', '=', class_id.id), ('academic_year_id', '=', aca_id.id), ('semester_id', '=', semister_id.id)])
        exam_type_ids = result_ids.mapped('exam_type_id')
        course_name_ids = cource_id
        student_data = []
        student_ids = student_id
        for student in student_ids:
            student_dict = {'student_id': student.id, 'admission_id': student.student_id, 'student_name': student.student_name_id.name}
            cource_dict = []
            all_line_not_available = []
            for cource in course_name_ids:

                exam_type_dict = []
                exam_type_ids_data = result_ids.filtered(lambda x:x.course_name_id.id == cource.id and x.status in ['dean_approval', 'approved', 'ar_approved']).mapped('exam_type_id')
                for exam_type in exam_type_ids_data:
                    exam_type_id = result_ids.filtered(lambda x:x.exam_type_id.id == exam_type.id and x.course_name_id.id == cource.id and x.status in ['dean_approval', 'approved', 'ar_approved'])
                    if exam_type_id:
                        exam_line_id = exam_type_id[0].mapped('student_ids').filtered(lambda x:x.student_id.id == student.id)
                        if exam_line_id:
                            all_line_not_available.append(True)
                        else:
                            all_line_not_available.append(False)
                        exam_type_dict.append({'exam_type':exam_type.id, 'exam_line_id':exam_line_id})
                    else:
                        exam_line_id = False
                        all_line_not_available.append(False)
                cource_dict.append({'exam_records': exam_type_dict})
            student_dict.update({'cource_records': cource_dict})
            if any(all_line_not_available):
                student_data.append(student_dict)

        values = {
            'class_id': class_id.id,
            'aca_id': aca_id.id,
            'semister_id': semister_id.id,
            'student_data': student_data,
            'result_ids': result_ids,
            'course_name_ids': course_name_ids,
            'exam_type_ids': exam_type_ids,
            'total_exam_type': str(len(exam_type_ids) + 1)
        }
        return request.render("tvet_management.examination_result", values)

    @http.route(['/examination/student/view/<int:class_id>/<int:aca_id>/<int:semister_id>/<int:student_id>/','/examination/student/view/page/<int:page>'], type='http', auth="user", website=True)
    def portal_without_course_examination_view_class_adn_student(self, class_id, aca_id, semister_id, student_id, page=1,
                                                  date_begin=None, date_end=None, sortby=None, **kw):
        class_id = request.env['class.room'].sudo().browse(class_id)
        aca_id = request.env['academic.year'].sudo().browse(aca_id)
        semister_id = request.env['semester.semester'].sudo().browse(semister_id)
        student_id = request.env['student.registration'].sudo().browse(student_id)
        result_ids = request.env['exam.result'].sudo().search(
            [('class_id', '=', class_id.id), ('academic_year_id', '=', aca_id.id),
             ('semester_id', '=', semister_id.id)])
        cource_id = result_ids.mapped('course_name_id')
        # cource_id = request.env['course.subject'].sudo().browse(482)
        result_ids = request.env['exam.result'].sudo().search(
            [('class_id', '=', class_id.id), ('academic_year_id', '=', aca_id.id),
             ('semester_id', '=', semister_id.id)])
        exam_type_ids = result_ids.mapped('exam_type_id')
        course_name_ids = cource_id
        student_data = []
        student_ids = student_id
        for student in student_ids:
            student_dict = {'student_id': student.id, 'admission_id': student.student_id,
                            'student_name': student.student_name_id.name}
            cource_dict = []
            all_line_not_available = []
            for cource in course_name_ids:

                exam_type_dict = []
                exam_type_ids_data = result_ids.filtered(
                    lambda x: x.course_name_id.id == cource.id and x.status in ['dean_approval', 'approved',
                                                                                'ar_approved']).mapped('exam_type_id')
                for exam_type in exam_type_ids_data:
                    exam_type_id = result_ids.filtered(lambda
                                                           x: x.exam_type_id.id == exam_type.id and x.course_name_id.id == cource.id and x.status in [
                        'dean_approval', 'approved', 'ar_approved'])
                    if exam_type_id:
                        exam_line_id = exam_type_id[0].mapped('student_ids').filtered(
                            lambda x: x.student_id.id == student.id)
                        if exam_line_id:
                            all_line_not_available.append(True)
                        else:
                            all_line_not_available.append(False)
                        exam_type_dict.append({'exam_type': exam_type.id, 'exam_line_id': exam_line_id})
                    else:
                        exam_line_id = False
                        all_line_not_available.append(False)
                cource_dict.append({'exam_records': exam_type_dict})
            student_dict.update({'cource_records': cource_dict})
            if any(all_line_not_available):
                student_data.append(student_dict)

        values = {
            'class_id': class_id.id,
            'aca_id': aca_id.id,
            'semister_id': semister_id.id,
            'student_data': student_data,
            'result_ids': result_ids,
            'course_name_ids': course_name_ids,
            'exam_type_ids': exam_type_ids,
            'total_exam_type': str(len(exam_type_ids) + 1)
        }
        return request.render("tvet_management.examination_result", values)



    @http.route(['/exam_result/xlsx/<int:class_id>/<int:aca_id>/<int:semister_id>'], type='http', auth="user", website=True)
    def examination_xlsx(self, class_id, aca_id, semister_id):
        class_id = request.env['class.room'].sudo().browse(class_id)
        aca_id = request.env['academic.year'].sudo().browse(aca_id)
        semister_id = request.env['semester.semester'].sudo().browse(semister_id)
        result_ids = request.env['exam.result'].sudo().search([('class_id', '=', class_id.id), ('academic_year_id', '=', aca_id.id), ('semester_id', '=', semister_id.id)])
        datas = result_ids.sudo().generate_xlsx_report(class_id, aca_id, semister_id, result_ids)
        xls_filename = 'Examination Report.xlsx'
        response = request.make_response(datas,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition(xls_filename))
            ]
        )
        return response


    @http.route('/update/student_marks',type='json', auth="public", website=True)
    def update_marks(self,**kwargs):
        if kwargs.get('line_id'):
            if kwargs.get('value'):
                line = request.env['exam.result.entry.line'].browse(int(kwargs.get('line_id')))
                line.write({'marks': float(kwargs.get('value'))})
                if kwargs.get('line_ids'):
                    lines = ast.literal_eval(kwargs.get('line_ids'))
                    x = [int(n) for n in lines]
                    line_ids = request.env['exam.result.entry.line'].browse(x)
                    return {'total': str(float(sum(line_ids.mapped('marks'))))}
        return {'total': str(0.0)}



###################################Previous Class Code is started #####################################

    @http.route(
        ['/examination/student/previous/view/<int:class_id>/<int:aca_id>/<int:semister_id>/<int:previous_class_id>/',
         '/examination/previous/student/view/page/<int:page>'], type='http', auth="user", website=True)
    def portal_without_previous_class_with_course_examination_view_class_adn_student(self, class_id, aca_id,
                                                                                     semister_id, previous_class_id,
                                                                                     page=1,
                                                                                     date_begin=None, date_end=None,
                                                                                     sortby=None, **kw):
        lst = []
        class_id = request.env['class.room'].sudo().browse(class_id)
        lst.append(class_id.id)
        previous_class_ids = request.env['class.room'].sudo().browse(previous_class_id)
        lst.append(previous_class_ids.id)
        aca_id = request.env['academic.year'].sudo().browse(aca_id)
        semister_id = request.env['semester.semester'].sudo().browse(semister_id)
        result_ids = request.env['exam.result'].sudo().search(
            [('class_id', 'in', lst), ('academic_year_id', '=', aca_id.id),
             ('semester_id.sem_number', '=', semister_id.sem_number)])
        exam_type_ids = result_ids.mapped('exam_type_id')
        course_name_ids = result_ids.mapped('course_name_id')
        student_data = []
        student_data_ids = request.env['transfer.student'].sudo().search([('from_class_id', '=', previous_class_ids.id),('to_class_id', '=', class_id.id)])
        student_ids = request.env['student.registration'].sudo().search([('classroom_id', '=', class_id.id)])
        for student in student_ids:
            student_dict = {'student_id': student.id, 'admission_id': student.student_id,
                            'student_name': student.student_name_id.name}
            cource_dict = []
            all_line_not_available = []
            for cource in course_name_ids:
                exam_type_dict = []
                exam_type_ids_data = result_ids.filtered(
                    lambda x: x.course_name_id.id == cource.id and x.status in ['dean_approval', 'approved',
                                                                                'ar_approved']).mapped('exam_type_id')
                for exam_type in exam_type_ids_data:
                    exam_type_id = result_ids.filtered(lambda
                                                           x: x.exam_type_id.id == exam_type.id and x.course_name_id.id == cource.id and x.status in [
                        'dean_approval', 'approved', 'ar_approved'])
                    if exam_type_id:
                        total_student_ids = exam_type_id.mapped('student_ids')
                        exam_line_id = total_student_ids.filtered(
                            lambda x: x.student_id.id == student.id)
                        if exam_line_id:
                            all_line_not_available.append(True)
                        else:
                            all_line_not_available.append(False)
                        exam_type_dict.append({'exam_type': exam_type.id, 'exam_line_id': exam_line_id})
                    else:
                        exam_line_id = False
                        all_line_not_available.append(False)
                cource_dict.append({'exam_records': exam_type_dict})
            student_dict.update({'cource_records': cource_dict})
            if any(all_line_not_available):
                student_data.append(student_dict)

        values = {
            'class_id': class_id.id,
            'aca_id': aca_id.id,
            'semister_id': semister_id.id,
            'student_data': student_data,
            'result_ids': result_ids,
            'course_name_ids': course_name_ids,
            'exam_type_ids': exam_type_ids,
            'total_exam_type': str(len(exam_type_ids) + 1)
        }
        return request.render("tvet_management.examination_result", values)


    ############################# course is set ################################################
    @http.route(['/examination/previous/notstudent/view/<int:class_id>/<int:aca_id>/<int:semister_id>/<int:cource_id>/<int:previous_class_id>/',
                 '/examination/previous/student/not/view/page/<int:page>'], type='http', auth="user", website=True)
    def portal_examination_previous_class_student_is_not_set_view_classes(self, class_id, aca_id, semister_id, cource_id,previous_class_id, page=1, date_begin=None,
                                        date_end=None, sortby=None, **kw):
        lst = []
        class_id = request.env['class.room'].sudo().browse(class_id)
        lst.append(class_id.id)
        previous_class_ids = request.env['class.room'].sudo().browse(previous_class_id)
        lst.append(previous_class_ids.id)
        aca_id = request.env['academic.year'].sudo().browse(aca_id)
        semister_id = request.env['semester.semester'].sudo().browse(semister_id)
        cource_id = request.env['course.subject'].sudo().browse(cource_id)
        result_ids = request.env['exam.result'].sudo().search(
            [('class_id', 'in', lst), ('academic_year_id', '=', aca_id.id),
             ('semester_id.sem_number', '=', semister_id.sem_number)])
        print(result_ids, "resultids")
        exam_type_ids = result_ids.mapped('exam_type_id')
        course_name_ids = cource_id
        student_data = []
        student_data_ids = request.env['transfer.student'].sudo().search([('from_class_id', '=', previous_class_ids.id),('to_class_id', '=', class_id.id)])
        student_ids = request.env['student.registration'].sudo().search([('classroom_id', '=', class_id.id)])
        for student in student_ids:
            student_dict = {'student_id': student.id, 'admission_id': student.student_id,
                            'student_name': student.student_name_id.name}
            cource_dict = []
            all_line_not_available = []
            for cource in course_name_ids:

                exam_type_dict = []
                exam_type_ids_data = result_ids.filtered(
                    lambda x: x.course_name_id.id == cource.id and x.status in ['dean_approval', 'approved',
                                                                                'ar_approved']).mapped('exam_type_id')
                for exam_type in exam_type_ids_data:
                    exam_type_id = result_ids.filtered(lambda
                                                           x: x.exam_type_id.id == exam_type.id and x.course_name_id.id == cource.id and x.status in [
                        'dean_approval', 'approved', 'ar_approved'])
                    if exam_type_id:
                        total_student_ids = exam_type_id.mapped('student_ids')
                        exam_line_id = total_student_ids.filtered(
                            lambda x: x.student_id.id == student.id)
                        if exam_line_id:
                            all_line_not_available.append(True)
                        else:
                            all_line_not_available.append(False)
                        exam_type_dict.append({'exam_type': exam_type.id, 'exam_line_id': exam_line_id})
                    else:
                        exam_line_id = False
                        all_line_not_available.append(False)
                cource_dict.append({'exam_records': exam_type_dict})
            student_dict.update({'cource_records': cource_dict})
            if any(all_line_not_available):
                student_data.append(student_dict)

        values = {
            'class_id': class_id.id,
            'aca_id': aca_id.id,
            'semister_id': semister_id.id,
            'student_data': student_data,
            'result_ids': result_ids,
            'course_name_ids': course_name_ids,
            'exam_type_ids': exam_type_ids,
            'total_exam_type': str(len(exam_type_ids) + 1)
        }
        return request.render("tvet_management.examination_result", values)


    ################################################ previous class Details ##############################
    @http.route(['/examination/previous/student/view/previous/<int:class_id>/<int:aca_id>/<int:semister_id>/<int:cource_id>/<int:student_id>/<int:previous_class_id>/',
                 '/examination/previous/student/page/<int:page>'], type='http', auth="user", website=True)
    def portal_examination_view_class_courses_previous_class_show(self, class_id, aca_id, semister_id, cource_id,student_id,
                                                                  previous_class_id, page=1,
                                                                  date_begin=None, date_end=None, sortby=None, **kw):
        lst = []
        class_id = request.env['class.room'].sudo().browse(class_id)
        lst.append(class_id.id)
        previous_class_ids = request.env['class.room'].sudo().browse(previous_class_id)
        lst.append(previous_class_ids.id)
        aca_id = request.env['academic.year'].sudo().browse(aca_id)
        semister_id = request.env['semester.semester'].sudo().browse(semister_id)
        student_id = request.env['student.registration'].sudo().browse(student_id)
        cource_id = request.env['course.subject'].sudo().browse(cource_id)
        result_ids = request.env['exam.result'].sudo().search(
            [('class_id', 'in', lst), ('academic_year_id', '=', aca_id.id),
             ('semester_id.sem_number', '=', semister_id.sem_number)])
        exam_type_ids = result_ids.mapped('exam_type_id')
        course_name_ids = cource_id
        student_data = []
        student_data_ids = request.env['transfer.student'].sudo().search([('from_class_id', '=', previous_class_ids.id),('to_class_id', '=', class_id.id)])
        student_ids = student_id
        for student in student_ids:
            student_dict = {'student_id': student.id, 'admission_id': student.student_id,
                            'student_name': student.student_name_id.name}
            cource_dict = []
            all_line_not_available = []
            for cource in course_name_ids:

                exam_type_dict = []
                exam_type_ids_data = result_ids.filtered(
                    lambda x: x.course_name_id.id == cource.id and x.status in ['dean_approval', 'approved',
                                                                                'ar_approved']).mapped('exam_type_id')
                for exam_type in exam_type_ids_data:
                    exam_type_id = result_ids.filtered(lambda
                                                           x: x.exam_type_id.id == exam_type.id and x.course_name_id.id == cource.id and x.status in [
                        'dean_approval', 'approved', 'ar_approved'])
                    if exam_type_id:
                        total_student_ids = exam_type_id.mapped('student_ids')
                        exam_line_id = total_student_ids.filtered(
                            lambda x: x.student_id.id == student.id)
                        if exam_line_id:
                            all_line_not_available.append(True)
                        else:
                            all_line_not_available.append(False)
                        exam_type_dict.append({'exam_type': exam_type.id, 'exam_line_id': exam_line_id})
                    else:
                        exam_line_id = False
                        all_line_not_available.append(False)
                cource_dict.append({'exam_records': exam_type_dict})
            student_dict.update({'cource_records': cource_dict})
            if any(all_line_not_available):
                student_data.append(student_dict)

        values = {
            'class_id': class_id.id,
            'aca_id': aca_id.id,
            'semister_id': semister_id.id,
            'student_data': student_data,
            'result_ids': result_ids,
            'course_name_ids': course_name_ids,
            'exam_type_ids': exam_type_ids,
            'total_exam_type': str(len(exam_type_ids) + 1)
        }
        return request.render("tvet_management.examination_result", values)
