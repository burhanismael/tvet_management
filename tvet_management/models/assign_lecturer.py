# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import AccessError, UserError, ValidationError

class AssignLecturer(models.Model):
    _name = "assign.lecturer"
    _rec_name = 'lecturer_name_id'
    _description = "Assign Lecturer"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    status = fields.Selection([('draft','Draft'),('approved','Submit For Approval')], default="draft", tracking=True)
    lecturer_name_id = fields.Many2one('create.lecturer', string="Instructor Name" , tracking=True)
    school_department_id = fields.Many2one('school.department', string="Department Name", tracking=True, related='course_name_id.department_id')
    class_id = fields.Many2one('class.room', string="Batch Name", domain="[('school_department_id', '=', school_department_id)]", tracking=True)
    semester_id = fields.Many2one('semester.semester', string="Tier Name", domain="[('class_id', '=', class_id)]", tracking=True)
    course_name_id = fields.Many2one('course.subject', string="Course Name")
    # semester_id = fields.Many2one('semester.semester', tracking=True)
    assign_lecturer_line_ids = fields.One2many('assign.lecturer.line','assign_lecturer_id', string="Course", tracking=True)
    # compute = "_compute_action_course"
    course_ids = fields.Many2many('school.subject', string='Courses', tracking=True)

    @api.onchange('semester_id')
    def onchange_class_wise_semester(self):
        if self.semester_id:
            if self.class_id.semester_id.semester_name != self.semester_id.semester_name:
                raise ValidationError(_('This semester is not current semester!'))



    def _compute_action_course(self):
        for rec in self:
            self_id = rec.search([])
            for course in self_id:
                course_ids = []
                for line in course.assign_lecturer_line_ids:
                    course_ids += line.course_name_id.ids
                course.course_ids = course_ids
             
    def action_approve(self):
        course_lines = []
        for line in self.assign_lecturer_line_ids:
            course_lines.append((0, 0, {
                'lecturer_id' : self.lecturer_name_id.id,
                'class_id' : self.class_id.id,
                'semester_name_id' : self.semester_id.id,
                'course_id' : line.course_name_id.id
            }))
        vals = {
                'lecturer_name_id': self.lecturer_name_id.id,
                'school_department_id': self.school_department_id.id,
                'class_id': self.class_id.id,
                'semester_id' : self.semester_id.id,
                'approve_lecturer_line_ids' : course_lines,
            }
        self.env['approve.lecturer'].create(vals)
        self.status = 'approved'
        self.lecturer_name_id.is_assign_lecturer = True

    @api.onchange('school_department_id')
    def onchange_school_department(self):
        self.class_id = False
        self.semester_id = False

    @api.onchange('semester_id')
    def onchange_assign_lecturer(self):
        if self.assign_lecturer_line_ids:
            self.assign_lecturer_line_ids = False
            self.course_ids = False
        for rec in self:
            if rec.semester_id:
                course = rec.env['approve.course'].search([('class_id','=',rec.class_id.id),
                                                        ('semester_name_id', '=', rec.semester_id.id),
                                                        ('school_department_id', '=', rec.school_department_id.id),
                                                        ('status', '=', 'approved')])
                course_list = []

                for course_id in course:
                    for line in course_id.course_approve_line_ids:
                        for line_course_id in line.course:
                            course_list.append(line_course_id.id)
                            rec.update({
                                'assign_lecturer_line_ids': [(0, 0, {
                                            "course_name_id" : line_course_id.id,
                                            'course_code_id' : line_course_id.subject_code
                                        })],
                                })
                rec.course_ids = [(6, 0, course_list)]

class AssignLecturerLine(models.Model):
    _name = "assign.lecturer.line"
    _description = "Assign Lecturer Line"

    semeter_id = fields.Many2one('semester.semester', related='assign_lecturer_id.semester_id')
    course_name_id = fields.Many2one('school.subject', string="Subject Name", tracking=True)
    course_code_id = fields.Char(string="Subject Code", related="course_name_id.subject_code", tracking=True)
    assign_lecturer_id = fields.Many2one('assign.lecturer', tracking=True)

    @api.onchange('course_name_id')
    def sem_based_domain(self):
        if self.semeter_id:
            rooms_ids = self.assign_lecturer_id.class_id.class_room_ids.filtered(lambda x: x.semester_id.id == self.semeter_id.id)
            course_ids = rooms_ids.mapped('cource_ids')
            domain = [('id', 'in', course_ids.ids)]
            return {'domain': {'course_name_id': domain}}
