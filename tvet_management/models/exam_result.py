from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ExamResult(models.Model):
    _name = "exam.result.entry"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', copy=False, default='New', tracking=True)
    date = fields.Date(string='Date', tracking=True)
    department_id = fields.Many2one('school.department', string='Department', tracking=True)
    exam_type_id = fields.Many2one('exam.type', string="Exam Type", tracking=True)
    class_room_id = fields.Many2one('class.room', string="Batch Name", tracking=True)
    semester_id = fields.Many2one('semester.semester', string="Tier", tracking=True)
    course_subject_ids = fields.Many2many('school.subject', string="Course Name", compute="_compute_course_subject_ids", store=True, tracking=True)
    course_subject_id = fields.Many2one('school.subject', string="Subject Name", tracking=True)
    academic_year_id = fields.Many2one('academic.year', string="Academic Year", tracking=True)
    upload_file = fields.Binary(string="Upload file", tracking=True)
    student_ids = fields.One2many('exam.entry.line', 'exam_entry_id',
                                  string="Student", tracking=True)
    is_hide_result = fields.Boolean(string="IS Hide Result", tracking=True)
    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('approved', 'Confirmed')
        ], default="draft", copy=False, tracking=True)
    result_count = fields.Integer(string="Result Count", compute='_compute_result_count', tracking=True)

    @api.constrains('depreciation_move_ids')
    def _check_depreciations(self):
        for record in self:
            if record.state == 'open' and record.depreciation_move_ids and not record.currency_id.is_zero(
                    record.depreciation_move_ids.filtered(lambda x: not x.reversal_move_id).sorted(
                            lambda x: (x.date, x.id))[-1].asset_remaining_value):
                raise UserError(_("The remaining value on the last depreciation line must be 0"))

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        aca_id = self.env['res.config.settings'].search([('academic_year_id', '!=', False)], limit=1)
        if aca_id:
            vals['academic_year_id'] = aca_id.academic_year_id.id
        return vals

    @api.onchange('class_room_id')
    def class_based_domain(self):
        if self.class_room_id:
            semister_ids = self.class_room_id.class_room_ids.mapped('semester_id')
            domain = [('id', 'in', semister_ids.ids)]
            return {'domain': {'semester_id': domain}}
        # room_ids = self.env['class.room'].search([('name', '=', self.class_room_id.name)])
        # semister_ids = room_ids.mapped('semester_id')


    @api.onchange('semester_id')
    def semister_based_domain(self):
        if self.semester_id:
            rooms_ids = self.class_room_id.class_room_ids.filtered(lambda x: x.semester_id.id == self.semester_id.id)
            course_ids = rooms_ids.mapped('cource_ids')
            domain = [('id', 'in', course_ids.ids)]
            return {'domain': {'course_subject_id': domain}}

    @api.onchange('course_subject_id')
    def sem_based_domain(self):
        if self.semester_id:
            rooms_ids = self.class_room_id.class_room_ids.filtered(lambda x: x.semester_id.id == self.semester_id.id)
            course_ids = rooms_ids.mapped('cource_ids')
            domain = [('id', 'in', course_ids.ids)]
            return {'domain': {'course_subject_id': domain}}
        # room_ids = self.env['class.room'].search([('name', '=', self.class_room_id.name), ('semester_id', '=', self.semester_id.id)])
        # course_ids = room_ids.mapped('cource_ids')
        # domain = [('id', 'in', course_ids.ids)]
        # return {'domain': {'course_subject_id': domain}}

    @api.model
    def create(self, vals):
        code = self.env['ir.sequence'].next_by_code('exam.result.entry')
        vals['name'] = code

        a = self.search([('class_room_id', '=', vals.get('class_room_id')),
                         ('course_subject_id', '=', vals.get('course_subject_id')),
                         ('semester_id', '=', vals.get('semester_id')),
                         ('department_id', '=', vals.get('department_id')),
                         ('exam_type_id', '=', vals.get('exam_type_id')),
                         ('academic_year_id', '=', vals.get('academic_year_id'))
                         ])
        if a:
            raise ValidationError('this record already exist You can not create same record.')
        result_id = super(ExamResult, self).create(vals)
        return result_id

    def write(self, vals):
        for sale in self:
            if 'student_ids' in vals:
                for student_old in vals.get('student_ids'):
                    if student_old[2]:
                        old_id = sale.student_ids.filtered(lambda x: x.id == student_old[1])
                        if student_old[2].get('status'):
                            body = _(
                                '<span class="o_TrackingValue_oldValue me-1 px-1 text-muted fw-bold">%s</span> <i class="o_TrackingValue_separator fa fa-long-arrow-right mx-1 text-600" title="Changed" role="img" aria-label="Changed"></i> <span class="o_TrackingValue_newValue me-1 fw-bold text-info">%s</span> <span class="o_TrackingValue_fieldName ms-1 fst-italic text-muted">(Status)</span>') % (
                                str(old_id.student_id.student_name_id.name) + ' - ' + str(old_id.status), str(student_old[2].get('status')))
                            sale.message_post(body=body)
                        if student_old[2].get('room'):
                            body = _(
                                '<span class="o_TrackingValue_oldValue me-1 px-1 text-muted fw-bold">%s</span> <i class="o_TrackingValue_separator fa fa-long-arrow-right mx-1 text-600" title="Changed" role="img" aria-label="Changed"></i> <span class="o_TrackingValue_newValue me-1 fw-bold text-info">%s</span> <span class="o_TrackingValue_fieldName ms-1 fst-italic text-muted">(Room)</span>') % (
                                    str(old_id.student_id.student_name_id.name) + ' - ' + str(old_id.room), str(student_old[2].get('room')))
                            sale.message_post(body=body)
                        if student_old[2].get('note'):
                            body = _(
                                '<span class="o_TrackingValue_oldValue me-1 px-1 text-muted fw-bold">%s</span> <i class="o_TrackingValue_separator fa fa-long-arrow-right mx-1 text-600" title="Changed" role="img" aria-label="Changed"></i> <span class="o_TrackingValue_newValue me-1 fw-bold text-info">%s</span> <span class="o_TrackingValue_fieldName ms-1 fst-italic text-muted">(Note)</span>') % (
                                str(old_id.student_id.student_name_id.name) +' - '+ str(old_id.note), str(student_old[2].get('note')))
                            sale.message_post(body=body)

        return super(ExamResult, self).write(vals)

    @api.depends('class_room_id')
    def _compute_course_subject_ids(self):
        for result in self:
            class_room_id = result.env['class.room'].search([('id', '=', result.class_room_id.id)])
            course_ids = class_room_id.mapped('cource_ids')
            if course_ids:
                result.course_subject_ids = course_ids.ids
            else:
                result.course_subject_ids = []

    def _compute_result_count(self):
        for result in self:
            result_count = self.env['exam.result'].search_count([('entry_id', '=', self.id)])
            if result_count > 0:
                result.is_hide_result = True
            result.result_count = result_count


    def open_exam_result(self):
        result_ids = self.env['exam.result'].search([('entry_id', '=', self.id)])
        return {
            'name': _('Exam Result'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'exam.result',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', result_ids.ids)],
        }

    def action_approve(self):
        self.status = 'approved'

    # def unlink(self):
    #     for rec in self:
    #         if rec.status == 'approved' and not self.env.user.has_group('tvet_management.delete_records_exam_entry_access'):
    #             raise ValidationError('You can not delete This record Please contect Administator .')
    #     return super(ExamResult, self).unlink()

    @api.onchange('class_room_id')
    def onchange_class_id(self):
        for rec in self:
            if rec.class_room_id:
                rec.semester_id = rec.semester_id.id
                attendance_company = self.env.company.at_dance
                if rec.class_room_id:
                    student_ids = self.env['student.registration'].search(
                        [('classroom_id', '=', rec.class_room_id.id), ('status', '=', 'enrolled')])
                    list_line = []
                    for student in student_ids:
                        list_line.append((0, 0, {'student_id': student.id,
                                                 'registration_id': student.student_id,
                                                         'status': 'present',
                                                         'room': "",
                                                         'note': "",
                                                         }))
                for line in rec.student_ids:
                    line.unlink()
                rec.student_ids = list_line

    def action_create_result(self):
        view_id = self.env.ref('tvet_management.view_exam_result_entry_tree').id
        return {
            'res_model': 'exam.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('tvet_management.view_exam_result_entry_form').id,
            'context': {'department_id' : self.department_id.id, 
                        'exam_type_id' : self.exam_type_id.id,
                        'class_id': self.class_room_id.id,
                        'academic_year_id': self.academic_year_id.id,
                        'semester_id': self.semester_id.id,
                        'course_name_id': self.course_subject_id.id,
                        'entry_id': self.id,
                        'academic_year_id': self.academic_year_id.id,
                        'student_ids': self.student_ids.ids,
                        },
        }

    # def search(self, args, **kwargs):
    #     if self.env.user.has_group('tvet_management.lecturer_access') and not self.env.user.has_group('base.group_system'):
    #         lecturer_id = self.env['create.lecturer'].search([('user_id', '=', self.env.user.id)])
    #         approve_lecturer_id = self.env['approve.lecturer'].search([('lecturer_name_id', '=', lecturer_id.id)])
    #         course_ids = approve_lecturer_id.approve_lecturer_line_ids.mapped('course_id')
    #         class_room_ids = approve_lecturer_id.approve_lecturer_line_ids.mapped('class_id')
    #         args += [('course_subject_id', 'in', course_ids.ids), ('class_room_id', 'in', class_room_ids.ids)]
    #     return super(ExamResult, self).search(args, **kwargs)



class AttendanceAddSheetLine(models.Model):
    _name = "exam.entry.line"

    exam_entry_id = fields.Many2one('exam.result.entry', tracking=True)
    student_id = fields.Many2one('student.registration', string="Student", tracking=True)
    status = fields.Selection([('present', 'Present'), ('absent', 'Absent')], 'Status', default='present', tracking=True)
    room = fields.Char('Room', tracking=True)
    note = fields.Char('Note', tracking=True)
    registration_id = fields.Char('student id', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            exam_entry_line = self.env['exam.entry.line'].search([('exam_entry_id', '=', vals.get('exam_entry_id')), (
            'registration_id', '=', vals.get('registration_id'))])
            if exam_entry_line:
                raise ValidationError(
                    _('%s line is already exist Please remove this line.' % vals.get('registration_id')))
            else:
                exam_entry_id = self.env['exam.result.entry'].browse(vals.get('exam_entry_id'))
                registration_id = self.env['student.registration'].search(
                    [('student_id', '=', vals.get('registration_id')),
                     ('department_id', '=', exam_entry_id.department_id.id),
                     ('classroom_id', '=', exam_entry_id.class_room_id.id),
                     ('semester_id', '=', exam_entry_id.semester_id.id)])
                if registration_id:
                    vals['exam_entry_id'] = exam_entry_id.id
                    vals['student_id'] = registration_id.id
                    vals['registration_id'] = vals.get('registration_id')
                    vals['status'] = 'present'
        return super(AttendanceAddSheetLine, self).create(vals_list)
