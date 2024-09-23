# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AssignCourse(models.Model):
    _name = "assign.course"
    _rec_name = 'class_id'
    _description = "Assign Course"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([('draft', 'Draft'), ('approved', 'Submitted for Approval')], string="State",
                             default='draft', tracking=True)
    school_department_id = fields.Many2one('school.department', string="Department Name", tracking=True)
    class_id = fields.Many2one('class.room', string="Class Name",
                               domain="[('school_department_id', '=', school_department_id)]", tracking=True)
    # domain="[('shift_id.school_department_id', '=', school_department_id)]")
    school_shift_id = fields.Integer("---", tracking=True)
    semester_name_id = fields.Many2one('semester.semester', string="Semester Name",
                                       domain="[('class_id', '=', class_id)]", tracking=True)
    course_subject_line_ids = fields.One2many('assign.course.line', 'assign_course_id', string="Course", tracking=True)
    course_subject_id = fields.Many2many('school.subject', string='Subject', tracking=True)
    is_assign_course = fields.Boolean(default=False, tracking=True)
    aca_id = fields.Many2one('academic.year', string="Academic Year")

    # is_assign_course_check = fields.Boolean(default=False, compute='_compute_assign_course')

    # def _compute_assign_course(self):
    #     for rec in self:
    #         self_id = rec.search([('state', '=', 'approved'),('is_assign_course', '=', False)])
    #         if self_id:
    #             for assign_course in self_id:
    #                 approve_course = rec.env['approve.course'].search([
    #                                                 ('school_department_id', '=', assign_course.school_department_id.id),
    #                                                 ('class_id', '=', assign_course.class_id.id),
    #                                                 ('semester_name_id', '=', assign_course.semester_name_id.id),
    #                                                 ('status', '=', 'approved')])
    #                 if approve_course:
    #                     for course in approve_course:
    #                         for line in course.course_approve_line_ids:
    #                             if assign_course.course_subject_id.id == line.course.id:
    #                                 assign_course.is_assign_course = True
    #                                 assign_course.is_assign_course_check = True
    #                             else:
    #                                 assign_course.is_assign_course_check = False
    #                 else:
    #                     rec.is_assign_course_check = False
    #         else:
    #             rec.is_assign_course_check = False

    @api.constrains('school_department_id', 'class_id', 'semester_name_id', 'course_subject_id')
    def _check_duplicate(self):
        assign_course_id = self.env['assign.course'].search(
            [('school_department_id', '=', self.school_department_id.id),
             ('class_id', '=', self.class_id.id),
             ('semester_name_id', '=', self.semester_name_id.id),
             ('course_subject_id', '=', self.course_subject_id.ids)])
        if len(assign_course_id) > 1:
            raise ValidationError(_('Already Available!'))

    def action_approve(self):
        for rec in self:
            # course_lines = []
            # for line in self.course_subject_line_ids:
            #     course_lines.append((0, 0, {
            #         "course_name_id" : rec.class_id.id,
            #         "semester" : rec.semester_name_id.id,
            #         "course" : line.course_name_id.id,
            #     }))
            vals = {
                'school_department_id': rec.school_department_id.id,
                'class_id': rec.class_id.id,
                'semester_name_id': rec.semester_name_id.id,
                'aca_id': rec.aca_id.id,
                'course_approve_line_ids': [(0, 0, {
                    "course_name_id": rec.class_id.id,
                    "semester": rec.semester_name_id.id,
                    "course": [(6, 0, rec.course_subject_id.ids)],
                })]
            }
            self.env['approve.course'].create(vals)
            rec.state = 'approved'

    @api.onchange('school_department_id')
    def onchange_school_department_id(self):
        for rec in self:
            if rec.course_subject_line_ids:
                rec.course_subject_line_ids = False
            course = rec.env['school.subject'].search([('school_department_id', '=', rec.school_department_id.id)])
            if course:
                rec.school_department_id = course.school_department_id
            if course:
                for course_id in course:
                    rec.update({
                        'course_subject_line_ids': [(0, 0, {
                            "course_code": course_id.subject_code,
                            "course_name_id": course_id.id,
                            "credit_hrs": course_id.credit_hrs,
                            "remarks": course_id.remarks,
                        })],
                    })

    @api.onchange('school_department_id')
    def _onchange_course_subject_id(self):
        if self.school_department_id and self.school_department_id != self.class_id.school_department_id:
            self.class_id = False
            self.semester_name_id = False

    @api.onchange('class_id')
    def _onchange_academic_year_id(self):
        if self.class_id.school_department_id:
            self.school_department_id = self.class_id.school_department_id

        if self.class_id and self.class_id != self.semester_name_id.class_id:
            self.semester_name_id = False


class AssignCourse(models.Model):
    _name = "assign.course.line"
    _description = "Assign Course line"

    course_code = fields.Char(tracking=True)
    course_name_id = fields.Many2one('school.subject', string="Subject Name", tracking=True)
    credit_hrs = fields.Float(string="Credit Hrs", tracking=True)
    remarks = fields.Text(string="Remarks", tracking=True)
    assign_course_id = fields.Many2one('assign.course', tracking=True)
