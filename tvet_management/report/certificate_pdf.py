# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime



class CertificateTemplate(models.AbstractModel):
    _name = 'report.tvet_management.certificate_template'
    _description = 'Certificate Template'

    def suffix(self, d):
        return {1:'st',2:'nd',3:'rd'}.get(d%20, 'th')

    # def custom_strftime(format, t):
    #     return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))


    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        student_id = self.env['student.registration'].browse(data.get('student_id'))
        class_id = self.env['class.room'].browse(data.get('class_id'))
        previous_class_id = self.env['class.room'].browse(data.get('previous_class_id'))
        class_ids = []
        if previous_class_id:
            class_ids.append(previous_class_id.id)
        class_ids.append(class_id.id)
        is_medical = data.get('is_medical')
        serial_no = data.get('serial_no')
        is_eight = 6
        total_sem = 6
        # sem_data_id =
        date = datetime.strptime(data.get('date'), "%Y-%m-%d").date()
        # senete = sem_data_id.name
        # if sem_data_id.senet_number == 7:
        #     is_eight = 7
        #     total_sem = 8
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
        is_medical_ids = grading_policy_ids.filtered(lambda x: x.is_medical)
        grading_ids = grading_policy_ids.filtered(lambda x: not x.is_medical)
        ######## Eight sem details ###########
        eight_sem_list_data = []
        eight_sem_total_mark = 0
        eight_total_sem = 0
        eight_sem_gpa = 0
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
            data = {
                'code': cource.subject_code,
                'course_title': cource.name,
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
            data = {
                'code': cource.subject_code,
                'course_title': cource.name,
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
            data = {
                'code': cource.subject_code,
                'course_title': cource.name,
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
            data = {
                'code': cource.subject_code,
                'course_title': cource.name,
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
            data = {
                'code': cource.subject_code,
                'course_title': cource.name,
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
            data = {
                'code': cource.subject_code,
                'course_title': cource.name,
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
            data = {
                'code': cource.subject_code,
                'course_title': cource.name,
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
            data = {
                'code': cource.subject_code,
                'course_title': cource.name,
                'marks': total_mark,
                'grads': grade,
                'gpa': gpa,
            }
            first_sem_list_data.append(data)
        if first_sem_total_mark > 0:
            first_sem_gpa = first_sem_total_mark / first_total_sem
        else:
            first_sem_gpa = 0
        if total_sem == 8:
            total_sem_total = eight_sem_gpa + seven_sem_gpa + six_sem_gpa + fifth_sem_gpa + four_sem_gpa + three_sem_gpa + two_sem_gpa + first_sem_gpa
            if total_sem_total > 0:
                total_cgpa = total_sem_total / total_sem
            else:
                total_cgpa = 0
        else:
            total_sem_total =  six_sem_gpa + fifth_sem_gpa + four_sem_gpa + three_sem_gpa + two_sem_gpa + first_sem_gpa
            if total_sem_total > 0:
                total_cgpa = total_sem_total / total_sem
            else:
                total_cgpa = 0
        total_cgpa = round(total_cgpa, 2)
        award_system_id  = self.env['awarding.system'].search([('cgpa', '<=', total_cgpa), ('m_cgpa', '>=', total_cgpa),
                                                               ('is_madical', '=', is_medical)], limit=1)
        if award_system_id:
            award_name = award_system_id.award
        else:
            award_name = ''
        date1 = [self.suffix(date.day), str(date.day) if date.day > 9 else ('0' + str(date.day)), date.strftime("%B"), str(date.year)]
        date2 = [self.suffix(datetime.now().day), str(datetime.now().day) if datetime.now().day > 9 else ('0' + str(datetime.now().day)), datetime.now().strftime("%B"), str(datetime.now().year)]
        # num = sem_data_id.name[0]

        # certificate_name = self.env['certificate.name'].search([('active_bool','=', True)], limit=1)
        
        data = {
            # 'certificate_name': certificate_name,
            'student_id': student_id,
            'is_eight': is_eight,
            # 'senete': senete,
            'date': date,
            'award_name': award_name,
            'serial_no': serial_no,
            'date1': date1,
            'date2': date2,
            # 'num':num,
        }
        return data
