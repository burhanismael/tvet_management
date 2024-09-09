# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class ApproveLecturer(models.Model):
    _name = "approve.lecturer"
    _rec_name = 'lecturer_name_id'
    _description = "Approve Lecturer"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    status = fields.Selection([('draft','Draft'),('approve','Approved'),('reject','Reject')], default='draft', tracking=True)
    lecturer_name_id = fields.Many2one('create.lecturer', tracking=True)
    school_department_id = fields.Many2one('school.department', string="Department Name", tracking=True)
    class_id = fields.Many2one('class.room', string="Class Name", domain="[('school_department_id', '=', school_department_id)]", tracking=True)
    semester_id = fields.Many2one('school.semester', domain="[('class_id', '=', class_id)]", tracking=True)
    approve_lecturer_line_ids = fields.One2many('approve.lecturer.line','approve_lecturer_id', string="Course", tracking=True)
    rejection_reason = fields.Text(string="Rejection Reason", tracking=True)

    def action_approve(self):
        self.status = 'approve'

    def reset_to_draft(self):
        for rec in self:
            rec.status = 'draft'

    def action_reject(self):
        for rec in self:
            if not rec.rejection_reason:
                raise ValidationError("Enter Valid Rejection Reason")
            rec.status = 'reject'

    @api.onchange('school_department_id')
    def onchange_school_department(self):
        self.class_id = False
        self.semester_id = False

    @api.onchange('semester_id')
    def onchange_assign_lecturer(self):
        if self.approve_lecturer_line_ids:
            self.approve_lecturer_line_ids = False
        for rec in self:
            if rec.semester_id:
                course = rec.env['assign.lecturer'].search([('class_id','=',rec.class_id.id),
                                                            ('semester_id', '=', rec.semester_id.id),
                                                            ('school_department_id', '=', rec.school_department_id.id),
                                                            ('lecturer_name_id', '=', rec.lecturer_name_id.id),
                                                            ('status', '=', 'approved')])
                for course_id in course:
                    for line in course_id.assign_lecturer_line_ids:
                        rec.update({
                            'approve_lecturer_line_ids': [(0, 0, {
                                        'lecturer_id' : rec.lecturer_name_id.id,
                                        'class_id' : rec.class_id.id,
                                        'semester_name_id' : rec.semester_id,
                                        'course_id' : line.course_name_id.id
                                    })],
                            })


class ApproveLecturerLine(models.Model):
    _name = "approve.lecturer.line"
    _description = "Assign Lecturer Line"

    lecturer_id = fields.Many2one('create.lecturer', string="Lacturer Name", tracking=True)
    class_id = fields.Many2one('class.room', string="Class Name", tracking=True)
    semester_name_id = fields.Many2one('school.semester', domain="[('class_id', '=', class_id)]", tracking=True)
    course_id = fields.Many2one('school.course', string="Course Name", tracking=True)
    approve_lecturer_id = fields.Many2one('approve.lecturer', tracking=True)
