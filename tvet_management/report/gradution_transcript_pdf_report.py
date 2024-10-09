# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import calendar

class GradutionTranscriprtTemplate(models.AbstractModel):
    _name = 'report.bosaso_university.gradution_transcriprt_template'
    _description = 'Report Gradution Transcriprt Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        previous_class_id = self.env['class.room'].browse(data.get('previous_class_id'))
        class_id = self.env['class.room'].browse(data.get('class_id'))
        # class_ids = self.env['class.room'].browse(data.get('class_id'))
        sem_data = data.get('semister_id')
        issu_date = data.get('issu_date')
        is_eight = False
        if sem_data == 'eight':
            is_eight = True
        class_ids = []
        if previous_class_id:
            class_ids.append(previous_class_id.id)
        class_ids.append(class_id.id)
        student_id = self.env['student.registration'].browse(data.get('student_id'))
        student_exam_result_ids = self.env['exam.result.entry.line'].search([('student_id', '=', student_id.id)])
        first_sem_ids = student_exam_result_ids.filtered(lambda x:x.exam_result_entry_id.semester_id.sem_number == 1 and x.exam_result_entry_id.class_id.id in class_ids)
        second_sem_ids = student_exam_result_ids.filtered(lambda x:x.exam_result_entry_id.semester_id.sem_number == 2 and x.exam_result_entry_id.class_id.id in class_ids)
        third_sem_ids = student_exam_result_ids.filtered(lambda x:x.exam_result_entry_id.semester_id.sem_number == 3 and x.exam_result_entry_id.class_id.id in class_ids)
        fourth_sem_ids = student_exam_result_ids.filtered(lambda x:x.exam_result_entry_id.semester_id.sem_number == 4 and x.exam_result_entry_id.class_id.id in class_ids)
        fifth_sem_ids = student_exam_result_ids.filtered(lambda x:x.exam_result_entry_id.semester_id.sem_number == 5 and x.exam_result_entry_id.class_id.id in class_ids)
        six_sem_ids = student_exam_result_ids.filtered(lambda x:x.exam_result_entry_id.semester_id.sem_number == 6 and x.exam_result_entry_id.class_id.id in class_ids)
        seventh_sem_ids = student_exam_result_ids.filtered(lambda x:x.exam_result_entry_id.semester_id.sem_number == 7 and x.exam_result_entry_id.class_id.id in class_ids)
        eight_sem_ids = student_exam_result_ids.filtered(lambda x:x.exam_result_entry_id.semester_id.sem_number == 8 and x.exam_result_entry_id.class_id.id in class_ids)
        grading_policy_ids = self.env['grading.policy'].search([])
        grading_policy_ids = self.env['grading.policy'].search([])
        is_medical_ids = grading_policy_ids.filtered(lambda x: x.is_medical)
        grading_ids = grading_policy_ids.filtered(lambda x: not x.is_medical)
        ######## Eight sem details ###########
        eight_sem_list_data = []
        eight_sem_total_mark = 0
        eight_total_sem = 0
        eight_sem_gpa = 0
        total_creadit_hours = 0
        courcse_ids = eight_sem_ids.mapped('exam_result_entry_id').mapped('course_name_id')
        for cource in courcse_ids:
            gpa = 0.0
            grade = "F"
            eight_sem_course_ids = eight_sem_ids.filtered(
                lambda x: x.exam_result_entry_id.course_name_id.id == cource.id)
            exam_type_ids = eight_sem_ids.mapped('exam_result_entry_id').mapped('exam_type_id')
            maximum_mark = sum(exam_type_ids.mapped('maximum_mark'))
            total_mark = round(sum(eight_sem_course_ids.mapped('marks')), 2)
            marks = round(sum(eight_sem_course_ids.mapped('marks')), 2)
            total_sem_mark = round(marks, 2)
            if cource.is_medical == False:
                student_grading_ids = grading_ids.filtered(
                    lambda x: x.minimum <= total_sem_mark and x.maximum >= total_sem_mark)
                if student_grading_ids:
                    gpa = float(student_grading_ids[0].gpa)
                    grade = student_grading_ids[0].grade
                else:
                    gpa = 0.0
                    grade = "F"
            else:
                student_grading_ids = is_medical_ids.filtered(
                    lambda x: x.minimum <= total_sem_mark and x.maximum >= total_sem_mark)
                if student_grading_ids:
                    gpa = float(student_grading_ids[0].gpa)
                    grade = student_grading_ids[0].grade
                else:
                    gpa = 0.0
                    grade = "F"

            eight_sem_total_mark = eight_sem_total_mark + gpa
            eight_total_sem += 1
            total_creadit_hours += cource.credit_hrs
            data = {
                'code': cource.course_code,
                'course_title': cource.course_name,
                'marks': total_mark,
                'grads': grade,
                'gpa': gpa,
            }
            eight_sem_list_data.append(data)
        if eight_sem_total_mark > 0:
            eight_sem_gpa = eight_sem_total_mark / eight_total_sem
        else:
            eight_sem_gpa = 0
        ##################    SEVEN     ########################
        seven_sem_list_data = []
        seven_sem_total_mark = 0
        seven_total_sem = 0
        seven_sem_gpa = 0
        courcse_ids = seventh_sem_ids.mapped('exam_result_entry_id').mapped('course_name_id')
        for cource in courcse_ids:
            gpa = 0.0
            grade = "F"
            seven_sem_course_ids = seventh_sem_ids.filtered(
                lambda x: x.exam_result_entry_id.course_name_id.id == cource.id)
            exam_type_ids = seventh_sem_ids.mapped('exam_result_entry_id').mapped('exam_type_id')
            maximum_mark = sum(exam_type_ids.mapped('maximum_mark'))
            total_mark = round(sum(seven_sem_course_ids.mapped('marks')), 2)
            marks = round(sum(seven_sem_course_ids.mapped('marks')), 2)
            total_sem_mark = round(marks, 2)
            if cource.is_medical == False:
                student_grading_ids = grading_ids.filtered(
                    lambda x: x.minimum <= total_sem_mark and x.maximum >= total_sem_mark)
                if student_grading_ids:
                    gpa = float(student_grading_ids[0].gpa)
                    grade = student_grading_ids[0].grade
                else:
                    gpa = 0.0
                    grade = "F"
            else:
                student_grading_ids = is_medical_ids.filtered(
                    lambda x: x.minimum <= total_sem_mark and x.maximum >= total_sem_mark)
                if student_grading_ids:
                    gpa = float(student_grading_ids[0].gpa)
                    grade = student_grading_ids[0].grade
                else:
                    gpa = 0.0
                    grade = "F"

            seven_sem_total_mark = seven_sem_total_mark + gpa
            seven_total_sem += 1
            total_creadit_hours += cource.credit_hrs
            data = {
                'code': cource.course_code,
                'course_title': cource.course_name,
                'marks': total_mark,
                'grads': grade,
                'gpa': gpa,
            }
            seven_sem_list_data.append(data)
        if seven_sem_total_mark > 0:
            seven_sem_gpa = seven_sem_total_mark / seven_total_sem
        else:
            seven_sem_gpa = 0
        ###################     SIX     ###################
        six_sem_list_data = []
        six_sem_total_mark = 0
        six_total_sem = 0
        six_sem_gpa = 0
        courcse_ids = six_sem_ids.mapped('exam_result_entry_id').mapped('course_name_id')
        for cource in courcse_ids:
            gpa = 0.0
            grade = "F"
            six_sem_course_ids = six_sem_ids.filtered(lambda x: x.exam_result_entry_id.course_name_id.id == cource.id)
            exam_type_ids = six_sem_ids.mapped('exam_result_entry_id').mapped('exam_type_id')
            maximum_mark = sum(exam_type_ids.mapped('maximum_mark'))
            total_mark = round(sum(six_sem_course_ids.mapped('marks')), 2)
            marks = round(sum(six_sem_course_ids.mapped('marks')), 2)
            total_sem_mark = round(marks, 2)
            if cource.is_medical == False:
                student_grading_ids = grading_ids.filtered(
                    lambda x: x.minimum <= total_sem_mark and x.maximum >= total_sem_mark)
                if student_grading_ids:
                    gpa = float(student_grading_ids[0].gpa)
                    grade = student_grading_ids[0].grade
                else:
                    gpa = 0.0
                    grade = "F"
            else:
                student_grading_ids = is_medical_ids.filtered(
                    lambda x: x.minimum <= total_sem_mark and x.maximum >= total_sem_mark)
                if student_grading_ids:
                    gpa = float(student_grading_ids[0].gpa)
                    grade = student_grading_ids[0].grade
                else:
                    gpa = 0.0
                    grade = "F"

            six_sem_total_mark = six_sem_total_mark + gpa
            six_total_sem += 1
            total_creadit_hours += cource.credit_hrs
            data = {
                'code': cource.course_code,
                'course_title': cource.course_name,
                'marks': total_mark,
                'grads': grade,
                'gpa': gpa,
            }
            six_sem_list_data.append(data)
        if six_sem_total_mark > 0:
            six_sem_gpa = six_sem_total_mark / six_total_sem
        else:
            six_sem_gpa = 0
        ###############     FIFTH     ###################
        fifth_sem_list_data = []
        fifth_sem_total_mark = 0
        fifth_total_sem = 0
        fifth_sem_gpa = 0
        courcse_ids = fifth_sem_ids.mapped('exam_result_entry_id').mapped('course_name_id')
        for cource in courcse_ids:
            gpa = 0.0
            grade = "F"
            fifth_sem_course_ids = fifth_sem_ids.filtered(
                lambda x: x.exam_result_entry_id.course_name_id.id == cource.id)
            exam_type_ids = fifth_sem_ids.mapped('exam_result_entry_id').mapped('exam_type_id')
            maximum_mark = sum(exam_type_ids.mapped('maximum_mark'))
            total_mark = round(sum(fifth_sem_course_ids.mapped('marks')), 2)
            marks = round(sum(fifth_sem_course_ids.mapped('marks')), 2)
            total_sem_mark = round(marks, 2)
            if cource.is_medical == False:
                student_grading_ids = grading_ids.filtered(
                    lambda x: x.minimum <= total_sem_mark and x.maximum >= total_sem_mark)
                if student_grading_ids:
                    gpa = float(student_grading_ids[0].gpa)
                    grade = student_grading_ids[0].grade
                else:
                    gpa = 0.0
                    grade = "F"
            else:
                student_grading_ids = is_medical_ids.filtered(
                    lambda x: x.minimum <= total_sem_mark and x.maximum >= total_sem_mark)
                if student_grading_ids:
                    gpa = float(student_grading_ids[0].gpa)
                    grade = student_grading_ids[0].grade
                else:
                    gpa = 0.0
                    grade = "F"

            fifth_sem_total_mark = fifth_sem_total_mark + gpa
            fifth_total_sem += 1
            total_creadit_hours += cource.credit_hrs
            data = {
                'code': cource.course_code,
                'course_title': cource.course_name,
                'marks': total_mark,
                'grads': grade,
                'gpa': gpa,
            }
            fifth_sem_list_data.append(data)
        if fifth_sem_total_mark > 0:
            fifth_sem_gpa = fifth_sem_total_mark / fifth_total_sem
        else:
            fifth_sem_gpa = 0
        #######################   Four     #################################
        four_sem_list_data = []
        four_sem_total_mark = 0
        four_total_sem = 0
        four_sem_gpa = 0
        courcse_ids = fourth_sem_ids.mapped('exam_result_entry_id').mapped('course_name_id')
        for cource in courcse_ids:
            gpa = 0.0
            grade = "F"
            fourth_sem_course_ids = fourth_sem_ids.filtered(
                lambda x: x.exam_result_entry_id.course_name_id.id == cource.id)
            exam_type_ids = fourth_sem_ids.mapped('exam_result_entry_id').mapped('exam_type_id')
            maximum_mark = sum(exam_type_ids.mapped('maximum_mark'))
            total_mark = round(sum(fourth_sem_course_ids.mapped('marks')), 2)
            marks = round(sum(fourth_sem_course_ids.mapped('marks')), 2)
            total_sem_mark = round(marks, 2)
            if cource.is_medical == False:
                student_grading_ids = grading_ids.filtered(
                    lambda x: x.minimum <= total_sem_mark and x.maximum >= total_sem_mark)
                if student_grading_ids:
                    gpa = float(student_grading_ids[0].gpa)
                    grade = student_grading_ids[0].grade
                else:
                    gpa = 0.0
                    grade = "F"
            else:
                student_grading_ids = is_medical_ids.filtered(
                    lambda x: x.minimum <= total_sem_mark and x.maximum >= total_sem_mark)
                if student_grading_ids:
                    gpa = float(student_grading_ids[0].gpa)
                    grade = student_grading_ids[0].grade
                else:
                    gpa = 0.0
                    grade = "F"

            four_sem_total_mark = four_sem_total_mark + gpa
            four_total_sem += 1
            total_creadit_hours += cource.credit_hrs
            data = {
                'code': cource.course_code,
                'course_title': cource.course_name,
                'marks': total_mark,
                'grads': grade,
                'gpa': gpa,
            }
            four_sem_list_data.append(data)
        if four_sem_total_mark > 0:
            four_sem_gpa = four_sem_total_mark / four_total_sem
        else:
            four_sem_gpa = 0
        ##################    THIRD     ##############################
        three_sem_list_data = []
        three_sem_total_mark = 0
        three_total_sem = 0
        three_sem_gpa = 0
        courcse_ids = third_sem_ids.mapped('exam_result_entry_id').mapped('course_name_id')
        for cource in courcse_ids:
            gpa = 0.0
            grade = "F"
            third_sem_course_ids = third_sem_ids.filtered(
                lambda x: x.exam_result_entry_id.course_name_id.id == cource.id)
            exam_type_ids = third_sem_ids.mapped('exam_result_entry_id').mapped('exam_type_id')
            maximum_mark = sum(exam_type_ids.mapped('maximum_mark'))
            total_mark = round(sum(third_sem_course_ids.mapped('marks')), 2)
            marks = round(sum(third_sem_course_ids.mapped('marks')), 2)
            total_sem_mark = round(marks, 2)
            if cource.is_medical == False:
                student_grading_ids = grading_ids.filtered(
                    lambda x: x.minimum <= total_sem_mark and x.maximum >= total_sem_mark)
                if student_grading_ids:
                    gpa = float(student_grading_ids[0].gpa)
                    grade = student_grading_ids[0].grade
                else:
                    gpa = 0.0
                    grade = "F"
            else:
                student_grading_ids = is_medical_ids.filtered(
                    lambda x: x.minimum <= total_sem_mark and x.maximum >= total_sem_mark)
                if student_grading_ids:
                    gpa = float(student_grading_ids[0].gpa)
                    grade = student_grading_ids[0].grade
                else:
                    gpa = 0.0
                    grade = "F"

            three_sem_total_mark = three_sem_total_mark + gpa
            three_total_sem += 1
            total_creadit_hours += cource.credit_hrs
            data = {
                'code': cource.course_code,
                'course_title': cource.course_name,
                'marks': total_mark,
                'grads': grade,
                'gpa': gpa,
            }
            three_sem_list_data.append(data)
        if three_sem_total_mark > 0:
            three_sem_gpa = three_sem_total_mark / three_total_sem
        else:
            three_sem_gpa = 0
        #############    TWO     ###################
        two_sem_list_data = []
        two_sem_total_mark = 0
        two_total_sem = 0
        two_sem_gpa = 0
        courcse_ids = second_sem_ids.mapped('exam_result_entry_id').mapped('course_name_id')
        for cource in courcse_ids:
            gpa = 0.0
            grade = "F"
            second_sem_course_ids = second_sem_ids.filtered(
                lambda x: x.exam_result_entry_id.course_name_id.id == cource.id)
            exam_type_ids = second_sem_course_ids.mapped('exam_result_entry_id').mapped('exam_type_id')
            maximum_mark = sum(exam_type_ids.mapped('maximum_mark'))
            total_mark = round(sum(second_sem_course_ids.mapped('marks')), 2)
            marks = round(sum(second_sem_course_ids.mapped('marks')), 2)
            total_sem_mark = round(marks, 2)
            if cource.is_medical == False:
                student_grading_ids = grading_ids.filtered(
                    lambda x: x.minimum <= total_sem_mark and x.maximum >= total_sem_mark)
                if student_grading_ids:
                    gpa = float(student_grading_ids[0].gpa)
                    grade = student_grading_ids[0].grade
                else:
                    gpa = 0.0
                    grade = "F"
            else:
                student_grading_ids = is_medical_ids.filtered(
                    lambda x: x.minimum <= total_sem_mark and x.maximum >= total_sem_mark)
                if student_grading_ids:
                    gpa = float(student_grading_ids[0].gpa)
                    grade = student_grading_ids[0].grade
                else:
                    gpa = 0.0
                    grade = "F"

            two_sem_total_mark = two_sem_total_mark + gpa
            two_total_sem += 1
            total_creadit_hours += cource.credit_hrs
            data = {
                'code': cource.course_code,
                'course_title': cource.course_name,
                'marks': total_mark,
                'grads': grade,
                'gpa': gpa,
            }
            two_sem_list_data.append(data)
        if two_sem_total_mark > 0:
            two_sem_gpa = two_sem_total_mark / two_total_sem
        else:
            two_sem_gpa = 0
        ##############  FIRST  #######################
        first_sem_list_data = []
        first_sem_total_mark = 0
        first_total_sem = 0
        first_sem_gpa = 0
        courcse_ids = first_sem_ids.mapped('exam_result_entry_id').mapped('course_name_id')
        for cource in courcse_ids:
            gpa = 0.0
            grade = "F"
            first_sem_course_ids = first_sem_ids.filtered(
                lambda x: x.exam_result_entry_id.course_name_id.id == cource.id)
            exam_type_ids = first_sem_course_ids.mapped('exam_result_entry_id').mapped('exam_type_id')
            maximum_mark = sum(exam_type_ids.mapped('maximum_mark'))
            total_mark = round(sum(first_sem_course_ids.mapped('marks')), 2)
            marks = round(sum(first_sem_course_ids.mapped('marks')), 2)
            total_sem_mark = round(marks, 2)
            if cource.is_medical == False:
                student_grading_ids = grading_ids.filtered(
                    lambda x: x.minimum <= total_sem_mark and x.maximum >= total_sem_mark)
                if student_grading_ids:
                    gpa = float(student_grading_ids[0].gpa)
                    grade = student_grading_ids[0].grade
                else:
                    gpa = 0.0
                    grade = "F"
            else:
                student_grading_ids = is_medical_ids.filtered(
                    lambda x: x.minimum <= total_sem_mark and x.maximum >= total_sem_mark)
                if student_grading_ids:
                    gpa = float(student_grading_ids[0].gpa)
                    grade = student_grading_ids[0].grade
                else:
                    gpa = 0.0
                    grade = "F"

            first_sem_total_mark = first_sem_total_mark + gpa
            first_total_sem += 1
            total_creadit_hours += cource.credit_hrs
            data = {
                'code': cource.course_code,
                'course_title': cource.course_name,
                'marks': total_mark,
                'grads': grade,
                'gpa': gpa,
            }
            first_sem_list_data.append(data)
        if first_sem_total_mark > 0:
            first_sem_gpa = first_sem_total_mark / first_total_sem
        else:
            first_sem_gpa = 0
        if is_eight:
            total_sem_total = eight_sem_gpa + seven_sem_gpa + six_sem_gpa + fifth_sem_gpa + four_sem_gpa + three_sem_gpa + two_sem_gpa + first_sem_gpa
            if total_sem_total > 0:
                total_cgpa = total_sem_total / 8
            else:
                total_cgpa = 0
        else:
            total_sem_total =  six_sem_gpa + fifth_sem_gpa + four_sem_gpa + three_sem_gpa + two_sem_gpa + first_sem_gpa
            if total_sem_total > 0:
                total_cgpa = total_sem_total / 6
            else:
                total_cgpa = 0
        total_cgpa = round(total_cgpa, 2)
        data = {
            'class': class_id,
            'student_id': student_id,
            'first_sem_ids': first_sem_ids,
            'second_sem_ids': second_sem_ids,
            'third_sem_ids': third_sem_ids,
            'fourth_sem_ids': fourth_sem_ids,
            'fifth_sem_ids': fifth_sem_ids,
            'six_sem_ids': six_sem_ids,
            'seventh_sem_ids': seventh_sem_ids,
            'eight_sem_ids': eight_sem_ids,
            'is_eight': is_eight,
            'issu_date': issu_date,

            'eight_sem_data': eight_sem_list_data,
            'seven_sem_data': seven_sem_list_data,
            'six_sem_data': six_sem_list_data,
            'fifth_sem_data': fifth_sem_list_data,
            'four_sem_data': four_sem_list_data,
            'thrd_sem_data': three_sem_list_data,
            'sec_sem_data': two_sem_list_data,
            'fst_sem_data': first_sem_list_data,

            'eight_sem_gpa': eight_sem_gpa,
            'seven_sem_gpa': seven_sem_gpa,
            'six_sem_gpa': six_sem_gpa,
            'fifth_sem_gpa': fifth_sem_gpa,
            'four_sem_gpa': four_sem_gpa,
            'three_sem_gpa': three_sem_gpa,
            'two_sem_gpa': two_sem_gpa,
            'first_sem_gpa': first_sem_gpa,
            'total_cgpa': total_cgpa,
            'total_creadit_hours': total_creadit_hours
        }
        return data
