# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AttendanceSheet(models.Model):
    _name = "attendance.sheet"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _domain_class(self):
        class_domain = []
        assign_lecturer_ids = self.env['assign.lecturer'].search([('lecturer_name_id.user_id', '=', self.env.user.id), ('status', '=', 'approved')])
        for lacturer in assign_lecturer_ids:
            if lacturer.class_id.semester_id == lacturer.semester_id:
                class_domain.append(lacturer.class_id.id)
        if assign_lecturer_ids:
            return [('id', 'in', class_domain)]
        else:
            return []

    name = fields.Char('Name', copy=False, default='New', tracking=True)
    school_department_id = fields.Many2one('school.department', string="Department Name", tracking=True)
    class_id = fields.Many2one('class.room', string="Class Name",domain=_domain_class, tracking=True)
    student_ids = fields.One2many('attendance.sheet.line','attendance_sheet_id', string="Student", tracking=True)
    date = fields.Date(required=True, default=lambda self: fields.Date.context_today(self), tracking=True)
    status = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed')], default="draft", tracking=True)
    session = fields.Selection([('1', "First Session"),('2', "Second Session"),('3', "Third Session")], default='1')

    # def search(self, args, **kwargs):
    #     if not self.env.user.has_group('base.group_system') and not self.env.user.has_group('tvet_management.deans_access') and not self.env.user.has_group('tvet_management.academic_registerer_access') and not self.env.user.has_group('tvet_management.administrative_assistant_access') and not self.env.user.has_group('tvet_management.university_group_access'):
    #         args += [('create_uid', '=', self.env.user.id)]
    #     return super(AttendanceSheet, self).search(args, **kwargs)


    def action_draft(self):
        self.status = 'draft'

    def action_confirm(self):
        self.status = 'confirm'

    @api.onchange('class_id')
    def onchange_class_id(self):
        print("11111111111111111111111111111111")
        for rec in self:
            print('22222222222222222222222222222222222222222222222222222222222222222222')
            semester_id = self.env['semester.semester'].search([('class_id', '=', rec.class_id.id)])
            print("333333333333333333333333333333333333333333333333333333333333333333333333333", semester_id)
            rec.semester_id = semester_id.ids
            print("444444444444444444444444444444444444444444444444", rec.semester_id)
            if rec.class_id:
                print("555555555555555555555555555555555555555555555555555555555555555")
                student_ids = self.env['student.registration'].search([('classroom_id', '=', rec.class_id.id), ('status', '=', 'enrolled')])
                print("666666666666666666666666666666666666666666666666666666666666", student_ids)
                list_line = []
                for s in student_ids:
                    list_line.append((0, 0, {'student_id': s.id,
                                             'class_id': rec.class_id.id,
                                             'date': rec.date,
                                             'semester_id': rec.semester_id,
                                             'course_name_id': rec.course_name_id.id,
                                             }))
                for line in rec.student_ids:
                    line.unlink()
                rec.student_ids = list_line
        self.semester_id = self.class_id.semester_id.id


    semester_id = fields.Many2one('semester.semester', string="Semester Name", readonly=True)

    def _domain_course(self):
        approve_lecturer_line_ids = self.env['approve.lecturer.line'].search([('lecturer_id.user_id', '=', self.env.user.id)])
        return [('id', 'in', approve_lecturer_line_ids.mapped('course_id').ids)]

    course_name_id = fields.Many2one('school.subject', string="Subject Name")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('attendance.sheet') or _('New')
        res = super(AttendanceSheet, self).create(vals)
        return res

    @api.onchange('class_id')
    def domain_semseter_data(self):
        if self.class_id:
            approve_lecturer_line_ids = self.env['approve.lecturer.line'].search([('lecturer_id.user_id', '=', self.env.user.id), ('approve_lecturer_id.status', '=', 'approve'), ('class_id', '=', self.class_id.id)])
            domain = [('id', 'in', approve_lecturer_line_ids.mapped('semester_name_id').ids)]
            return {'domain': {'semester_id': domain}}

    @api.onchange('class_id', 'semester_id')
    def domain_class_data(self):
        if self.class_id and self.semester_id:
            approve_lecturer_line_ids = self.env['approve.lecturer.line'].search([('lecturer_id.user_id', '=', self.env.user.id), ('approve_lecturer_id.status', '=', 'approve'), ('class_id', '=', self.class_id.id), ('semester_name_id', '=', self.semester_id.id)])
            domain = [('id', 'in', approve_lecturer_line_ids.mapped('course_id').ids)]
            return {'domain': {'course_name_id': domain}}


    # def unlink(self):
    #     for rec in self:
    #         if self.env.user.has_group('tvet_management.lecturer_access'):
    #             raise ValidationError('You can not delete This record Please contect Administator .')
    #     return super(AttendanceSheet, self).unlink()

    @api.constrains('date')
    def _check_value(self):
        dublicate_id = self.env['attendance.sheet'].search([('class_id', '=', self.class_id.id),
                                                               ('semester_id', '>=', self.semester_id.id),
                                                               ('course_name_id', '<=', self.course_name_id.id),
                                                               ('date', '=', self.date),
                                                                ('session', '=', self.session)])

        if len(dublicate_id) >1:
            raise ValidationError('This record is already exist.')


class AttendanceSheetLine(models.Model):
    _name = "attendance.sheet.line"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    attendance_sheet_id = fields.Many2one('attendance.sheet', tracking=True)
    student_id = fields.Many2one('student.registration', string="Student", tracking=True)
    period = fields.Integer('Period', tracking=True)
    signature = fields.Char('Signature', tracking=True)
    checkbox = fields.Boolean('Present', default=True, tracking=True)
    checkbox2 = fields.Boolean('Absent', tracking=True)
    action_attandance = fields.Selection([('present', 'Present'), ('absent', 'Absent')], string="Attandance", tracking=True)
    remarks = fields.Char('Remarks', tracking=True)

    school_department_id = fields.Many2one('school.department', string="Department Name", tracking=True)
    class_id = fields.Many2one('class.room', string="Class Name", tracking=True)
    semester_id = fields.Many2one('semester.semester', string="Semester Name",
                                  domain="[('class_id', '=', class_id)]", tracking=True)
    course_name_id = fields.Many2one('school.subject', string="Subject Name", tracking=True)
    date = fields.Date('Date', tracking=True)
    checkbox3 = fields.Boolean('Absent Excused', tracking=True)

    @api.onchange('checkbox')
    def onchange_checkbox(self):

        for rec in self:
            if rec.checkbox:
                rec.checkbox2 = False
                rec.checkbox3 = False


    @api.onchange('checkbox2')
    def onchange_checkbox2(self):
        for rec in self:

            if rec.checkbox2:
                rec.checkbox = False
                rec.checkbox3 = False

    @api.onchange('checkbox3')
    def onchange_checkbox3(self):
        for rec in self:

            if rec.checkbox3:
                rec.checkbox = False
                rec.checkbox2 = False
