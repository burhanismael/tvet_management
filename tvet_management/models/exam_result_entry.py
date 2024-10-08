from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import json
import io
import pytz

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class ExamResultEntry(models.Model):
    _name = "exam.result"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', copy=False, default='New', tracking=True)
    department_id = fields.Many2one('school.department', string="Department Name", tracking=True)
    class_id = fields.Many2one('class.room', string="Class Name",
                               domain="[('school_department_id', '=', department_id)]", tracking=True)
    academic_year_id = fields.Many2one('academic.year', string="Academic Year", tracking=True)
    exam_type_id = fields.Many2one('exam.type', string="Exam Type", tracking=True)
    student_ids = fields.One2many('exam.result.entry.line', 'exam_result_entry_id',
                                  string="Student", tracking=True)
    semester_id = fields.Many2one('semester.semester', string="Semester Name",
                                  domain="[('class_id', '=', class_id)]", tracking=True)
    course_name_id = fields.Many2one('school.subject', string="Subject Name",
                                     domain="[('school_department_id', '=', department_id)]", tracking=True)
    type = fields.Selection([('lecturer_entry', 'Lecturer Entry'), ('management_entry', 'Management Entry')], 'Type',
                            tracking=True)
    entry_id = fields.Many2one('exam.result.entry', string="Entry", tracking=True)

    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('approved', 'Ar Approval'),
            ('ar_approved', 'Publish'),
        ], default="draft", copy=False, tracking=True)
    date = fields.Date(string="Date", default=fields.Date.today(), tracking=True)


    def write(self, vals):
        for sale in self:
            if 'student_ids' in vals:
                for student_old in vals.get('student_ids'):
                    if student_old[2]:
                        old_id = sale.student_ids.filtered(lambda x: x.id == student_old[1])
                        if student_old[2].get('marks'):
                            body = _(
                                '<span class="o_TrackingValue_oldValue me-1 px-1 text-muted fw-bold">%s</span> <i class="o_TrackingValue_separator fa fa-long-arrow-right mx-1 text-600" title="Changed" role="img" aria-label="Changed"></i> <span class="o_TrackingValue_newValue me-1 fw-bold text-info">%s</span> <span class="o_TrackingValue_fieldName ms-1 fst-italic text-muted">(Marks)</span>') % (
                                str(old_id.student_id.student_name_id.name) + ' - ' + str(old_id.marks), str(student_old[2].get('marks')))
                            sale.message_post(body=body)
                        if student_old[2].get('remarks'):
                            body = _(
                                '<span class="o_TrackingValue_oldValue me-1 px-1 text-muted fw-bold">%s</span> <i class="o_TrackingValue_separator fa fa-long-arrow-right mx-1 text-600" title="Changed" role="img" aria-label="Changed"></i> <span class="o_TrackingValue_newValue me-1 fw-bold text-info">%s</span> <span class="o_TrackingValue_fieldName ms-1 fst-italic text-muted">(Remarks)</span>') % (
                                    str(old_id.student_id.student_name_id.name) + ' - ' + str(old_id.room), str(student_old[2].get('remarks')))
                            sale.message_post(body=body)
                        # if student_old[2].get('note'):
                        #     body = _(
                        #         '<span class="o_TrackingValue_oldValue me-1 px-1 text-muted fw-bold">%s</span> <i class="o_TrackingValue_separator fa fa-long-arrow-right mx-1 text-600" title="Changed" role="img" aria-label="Changed"></i> <span class="o_TrackingValue_newValue me-1 fw-bold text-info">%s</span> <span class="o_TrackingValue_fieldName ms-1 fst-italic text-muted">(Note)</span>') % (
                        #         str(old_id.student_id.student_name_id.name) +' - '+ str(old_id.note), str(student_old[2].get('note')))
                        #     sale.message_post(body=body)

        return super(ExamResultEntry, self).write(vals)

    # def unlink(self):
    #     for rec in self:
    #         if not self.env.user.has_group(
    #                 'tvet_management.delete_records_exam_entry_access'):
    #             raise ValidationError('You can not delete This record Please contect Administator .')
    #     return super(ExamResultEntry, self).unlink()

    def action_submit_for_approval(self):
        self.status = 'approved'


    def action_reject_by_dean(self):
        self.status = 'rejected'

    def action_ar_approved(self):
        self.status = 'ar_approved'

    def action_reject_approved(self):
        self.status = 'rejected'

    def action_to_draft(self):
        self.status = 'draft'


    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        if self.env.context.get('department_id'):
            vals['department_id'] = self.env.context.get('department_id')
        if self.env.context.get('class_id'):
            vals['class_id'] = self.env.context.get('class_id')
        if self.env.context.get('exam_type_id'):
            vals['exam_type_id'] = self.env.context.get('exam_type_id')
        if self.env.context.get('semester_id'):
            vals['semester_id'] = self.env.context.get('semester_id')
        if self.env.context.get('course_name_id'):
            vals['course_name_id'] = self.env.context.get('course_name_id')
        if self.env.context.get('entry_id'):
            vals['entry_id'] = self.env.context.get('entry_id')
        if self.env.context.get('academic_year_id'):
            vals['academic_year_id'] = self.env.context.get('academic_year_id')
        else:
            aca_id = self.env['res.config.settings'].search([('academic_year_id', '!=', False)])
            if aca_id:
                vals['academic_year_id'] = aca_id.academic_year_id.id
        if self.env.context.get('student_ids'):
            student_data = self.env.context.get('student_ids')
            student_ids = self.env['exam.entry.line'].browse(student_data)
            list_line = []
            for student in student_ids:
                list_line.append((0, 0, {'student_id': student.student_id.id,
                                         'registration_id': student.registration_id,
                                         'marks': 0.0,
                                         'remarks': "",
                                         }))
            vals['student_ids'] = list_line
        return vals

    @api.model
    def create(self, vals):
        code = self.env['ir.sequence'].next_by_code('exam.result')
        vals['name'] = code
        a = self.search([('academic_year_id', '=', vals.get('academic_year_id')),
                         ('exam_type_id', '=', vals.get('exam_type_id')),
                         ('department_id', '=', vals.get('department_id')),
                         ('class_id', '=', vals.get('class_id')),
                         ('semester_id', '=', vals.get('semester_id')),
                         ('course_name_id', '=', vals.get('course_name_id')),
                         ('date', '=', vals.get('date'))])
        if a:
            raise ValidationError('You can not create same record.')

        sem_name = self.env['semester.semester'].browse(vals.get('semester_id'))
        exam_type_name = self.env['exam.type'].browse(vals.get('exam_type_id'))
        dublicate = self.search([('academic_year_id', '=', vals.get('academic_year_id')),
                                 ('semester_id.semester_name', '=', sem_name.semester_name),
                                 ('class_id', '=', vals.get('class_id')),
                                 ('course_name_id', '=', vals.get('course_name_id')),
                                 ('department_id', '=', vals.get('department_id')),
                                 ('exam_type_id.exam_type', '=', exam_type_name.exam_type)
                                 ])
        if len(dublicate) >= 1:
            raise ValidationError('You can not create same record.')

        class_id = self.env['class.room'].search([('id', '=', vals.get('class_id'))])
        semester_ids = class_id.class_room_ids.mapped('semester_id')
        semester_id = self.env['semester.semester'].browse(vals.get('semester_id'))
        original_sem_id = self.env['semester.semester'].search(
                [('semester_name', '=', semester_id.semester_name), ('class_id', '=', class_id.id)], limit=1)
        # if not original_sem_id:
        #     raise ValidationError('semester is not find.')
        if original_sem_id and (original_sem_id.id not in semester_ids.ids):
            raise ValidationError('semester is not relevent to this Class.')
        line_ids = class_id.class_room_ids.filtered(lambda x:x.semester_id.id == original_sem_id.id)
        if line_ids:
            line_id = line_ids[0]
            course_ids = line_id.cource_ids.ids
            if vals.get('course_name_id') not in course_ids:
                raise ValidationError('Course is relevant to this semester and class.')
        result_id = super(ExamResultEntry, self).create(vals)
        
        # a = self.search([('academic_year_id', '=', result_id.academic_year_id.id),
        #                 ('exam_type_id', '=', result_id.exam_type_id.id),
        #                 ('department_id', '=', result_id.department_id.id),
        #                 ('class_id', '=', result_id.class_id.id),
        #                 ('semester_id', '=', result_id.semester_id.id),
        #                 ('course_name_id', '=', result_id.course_name_id.id)])
        # if a:
        #    raise ValidationError('You can not create same record.')

        if result_id.semester_id.class_id.id != result_id.class_id.id:
            semester_id = self.env['semester.semester'].search(
                [('semester_name', '=', result_id.semester_id.semester_name), ('class_id', '=', result_id.class_id.id)], limit=1)
            if semester_id:
                result_id.semester_id = semester_id.id
        return result_id

    def search(self, args, **kwargs):
        if self.env.user.has_group('tvet_management.lecturer_access') and not self.env.user.has_group(
                'base.group_system'):
            lecturer_id = self.env['create.lecturer'].search([('user_id', '=', self.env.user.id)])
            if lecturer_id:
                approve_lecturer_id = self.env['approve.lecturer'].search([('lecturer_name_id', '=', lecturer_id.id)])
                course_ids = approve_lecturer_id.approve_lecturer_line_ids.mapped('course_id')
                class_ids = approve_lecturer_id.approve_lecturer_line_ids.mapped('class_id')
                args += [('course_name_id', 'in', course_ids.ids), ('class_id', 'in', class_ids.ids)]
        return super(ExamResultEntry, self).search(args, **kwargs)

    @api.model
    def generate_xlsx_report(self, class_id, aca_id, semister_id, result_ids):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        format1 = workbook.add_format({'font_size': 10, 'valign': 'vcenter', 'align': 'center', 'bold': True})
        format2 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})
        format3 = workbook.add_format({'font_size': 10, 'align': 'left', })
        format4 = workbook.add_format({'font_size': 10, 'align': 'left', 'bold': True})
        sheet = workbook.add_worksheet("Examination Report")

        exam_type_ids = result_ids.mapped('exam_type_id')
        course_name_ids = result_ids.mapped('course_name_id')
        student_data = []
        student_ids = self.env['student.registration'].search([('classroom_id', '=', class_id.id)])
        for student in student_ids:
            student_dict = {'student_id': student.id, 'admission_id': student.student_id,
                            'student_name': student.student_name_id.name}
            cource_dict = []
            for cource in course_name_ids:
                exam_type_dict = []
                exam_type_ids_data = result_ids.filtered(lambda x: x.course_name_id.id == cource.id and x.status in ['approved', 'ar_approved']).mapped(
                    'exam_type_id')
                for exam_type in exam_type_ids_data:
                    exam_type_id = result_ids.filtered(
                        lambda x: x.exam_type_id.id == exam_type.id and x.course_name_id.id == cource.id and x.status in ['approved', 'ar_approved'])
                    if exam_type_id:
                        exam_line_id = exam_type_id[0].mapped('student_ids').filtered(
                            lambda x: x.student_id.id == student.id)
                        exam_type_dict.append({'exam_type': exam_type.id, 'exam_line_id': exam_line_id})
                    else:
                        exam_line_id = False
                cource_dict.append({'exam_records': exam_type_dict})
            student_dict.update({'cource_records': cource_dict})
            student_data.append(student_dict)

        main_row = 0
        main_col = 0
        row = 2
        col = 3

        sheet.merge_range(main_row, main_col, main_row, main_col + 30, "Examination Report", format1)
        course_col = len(exam_type_ids)
        for course in course_name_ids:
            course_col = len(result_ids.filtered(lambda x: x.course_name_id.id == course.id and x.status in ['approved', 'ar_approved']).mapped('exam_type_id'))
            sheet.merge_range(row, col, row, col + course_col, course.course_name, format2)
            col += course_col + 1

        sheet.write(row + 1, 0, '#', format4)
        sheet.set_column(0, 0, 10)
        sheet.write(row + 1, 1, 'StudentId', format4)
        sheet.set_column(1, 1, 15)
        sheet.write(row + 1, 2, 'Student Name', format4)
        sheet.set_column(2, 2, 20)

        exam_col = 3
        for course in course_name_ids:
            exam_type_ids_data = result_ids.filtered(lambda x: x.course_name_id.id == course.id and x.status in ['approved', 'ar_approved']).mapped('exam_type_id')
            for exam in exam_type_ids_data:
                sheet.write(row + 1, exam_col, exam.exam_type, format4)
                sheet.set_column(exam_col, exam_col, 10)
                exam_col += 1
            if len(exam_type_ids_data) > 0:
                sheet.write(row + 1, exam_col, "Total", format4)
            exam_col += 1

        row += 2
        index = 0
        for student in student_data:
            index += 1
            sheet.write(row, 0, index, format3)
            sheet.write(row, 1, student.get('admission_id'), format3)
            sheet.write(row, 2, student.get('student_name'), format3)
            s_col = 3
            for cource in student.get('cource_records'):
                total_mark = 0
                for exam_type in cource.get('exam_records'):
                    if exam_type.get('exam_line_id'):
                        for rec in exam_type.get('exam_line_id'):
                            total_mark = total_mark + rec.marks
                            sheet.write(row, s_col, rec.marks, format3)
                        s_col += 1
                    else:
                        sheet.write(row, s_col, 0, format3)
                        s_col += 1
                if len(cource.get('exam_records'))> 0:
                    sheet.write(row, s_col, total_mark, format3)
                s_col += 1
            row += 1

        workbook.close()
        return output.getvalue()


class AttendanceSheetLine(models.Model):
    _name = "exam.result.entry.line"

    registration_id = fields.Char('student id', tracking=True)
    exam_result_entry_id = fields.Many2one('exam.result', tracking=True)
    student_id = fields.Many2one('student.registration', string="Student", tracking=True)
    marks = fields.Float(string="Marks", tracking=True)
    remarks = fields.Char('Remark', tracking=True)

    @api.onchange('student_id')
    def get_student_reg_id(self):
        if self.student_id:
            self.registration_id = self.student_id.student_id
    @api.model
    def create(self, vals):
        line_ids = self.search([('registration_id', '=', vals.get('registration_id')),
                                ('exam_result_entry_id', '=', vals.get('exam_result_entry_id'))])
        line_ids.unlink()
        exam_result_entry_id = self.env['exam.result'].search([('id', '=', vals.get('exam_result_entry_id'))])
        a = self.env['exam.result'].search([
            ('class_id', '=', exam_result_entry_id.class_id.id),
            ('semester_id', '=', exam_result_entry_id.semester_id.id),
            ('academic_year_id', '=', exam_result_entry_id.academic_year_id.id),
            ('exam_type_id', '=', exam_result_entry_id.exam_type_id.id),
            ('course_name_id', '=', exam_result_entry_id.course_name_id.id),
            ('department_id', '=', exam_result_entry_id.department_id.id)])
        if len(a) > 1:
            raise ValidationError(_('This Record Already Available!'))
        rooms_ids = exam_result_entry_id.class_id.class_room_ids.filtered(lambda x: x.semester_id.id == exam_result_entry_id.semester_id.id)
        course_ids = rooms_ids.mapped('cource_ids')
        if exam_result_entry_id.course_name_id.id == course_ids:
            raise ValidationError(_('Course is not relevant to this Class!'))
        class_sem_id = self.env['semester.semester'].search([('class_id', '=', exam_result_entry_id.class_id.id), ('semester_name', '=', exam_result_entry_id.semester_id.semester_name)], limit=1)
        if class_sem_id and class_sem_id.academic_year_id.id != exam_result_entry_id.academic_year_id.id:
            raise ValidationError(_('Academic Year is not relevant to this Semester!'))
        if exam_result_entry_id.class_id.school_department_id.id != exam_result_entry_id.department_id.id:
            raise ValidationError(_('Department is not relevant to this Class!'))


        else:
            exam_result_entry_ids = self.env['exam.result'].browse(vals.get('exam_result_entry_id'))
            regi = self.env['student.registration'].search(
                [('student_id', '=', vals.get('registration_id')),
                 ('classroom_id', '!=', exam_result_entry_ids.class_id.id)])
            if regi:
                raise ValidationError('%s this Student id not exist in this class.' % vals.get('registration_id'))
            else:
                if vals.get('registration_id'):
                    registration_id = self.env['student.registration'].search(
                        [('student_id', '=', vals.get('registration_id'))])
                    if registration_id:
                        vals['exam_result_entry_id'] = exam_result_entry_ids.id
                        vals['student_id'] = registration_id.id
                        vals['registration_id'] = vals.get('registration_id')
                        vals['marks'] = vals.get('marks')
                        vals['remarks'] = vals.get('remarks')

        new_id = self.env['exam.result'].browse(vals.get('exam_result_entry_id'))

        rec = super(AttendanceSheetLine, self).create(vals)

        if rec.marks > new_id.exam_type_id.maximum_mark:
            raise ValidationError(_('Student Marks should not be greater then Exam Type Maximum Marks!'))
        return rec

    def write(self, values):
        if values.get('marks'):
            if values.get('marks') > self.exam_result_entry_id.exam_type_id.maximum_mark:
                raise ValidationError(("Student %s Marks not grater than Maximum Marks %s .") % (
                    self.student_id.student_name_id.name, self.exam_result_entry_id.exam_type_id.maximum_mark))
        if self.student_id:
            if self.student_id.classroom_id.id != self.exam_result_entry_id.class_id.id:
                raise ValidationError(("Student not relevent to this class ."))
        res = super(AttendanceSheetLine, self).write(values)
        return res

    @api.onchange('marks')
    def marks_velidation(self):
        if self.marks > self.exam_result_entry_id.exam_type_id.maximum_mark:
            raise ValidationError(("Student %s Marks not grater than Maximum Marks %s .") % (
                self.student_id.student_name_id.name, self.exam_result_entry_id.exam_type_id.maximum_mark))

    @api.onchange('student_id')
    def marks_velidation(self):
        if self.student_id:
            if self.student_id.classroom_id.id != self.exam_result_entry_id.class_id.id:
                raise ValidationError(("Student not relevent to this class ."))
