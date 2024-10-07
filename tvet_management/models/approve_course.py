# -*- coding: utf-8 -*-
import reportlab.platypus
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ApproveCourse(models.Model):
    _name = "approve.course"
    _rec_name = 'class_id'
    _description = "Assign Course"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    status = fields.Selection([('draft', 'To Be Approved'), ('approved', 'Approved'), ('reject', 'Reject')],
                              default='draft', tracking=True)
    school_department_id = fields.Many2one('school.department', string="Department Name", tracking=True)
    class_id = fields.Many2one('class.room', string="Class Name",
                               domain="[('school_department_id', '=', school_department_id)]", tracking=True)
    semester_name_id = fields.Many2one('semester.semester', string="Semester Name",
                                       domain="[('class_id', '=', class_id)]", tracking=True)
    course_approve_line_ids = fields.One2many('approve.course.line', 'assign_course_id', string="Course", tracking=True)
    aca_id = fields.Many2one('academic.year', string="Academic Year")

    def action_course_approve(self):
        course = self.env['assign.course'].search([
            ('school_department_id', '=', self.school_department_id.id),
            ('is_assign_course', '=', False),
            ('class_id', '=', self.class_id.id),
            ('semester_name_id', '=', self.semester_name_id.id),
            ('state', '=', 'approved')], limit=1)
        course.is_assign_course = True

        for record in self:
            dublicate_record = record.class_id.class_room_ids.filtered(
                lambda r: r.semester_id.id == record.semester_name_id.id and all(
                    course_id in r.cource_ids.ids for course_id in record.course_approve_line_ids.course.ids))
            if dublicate_record:
                raise ValidationError("A record with the same semester and courses already exists.")
            existing_record = record.class_id.class_room_ids.filtered(
                lambda r: r.semester_id.id == record.semester_name_id.id)
            if existing_record:
                existing_record.write(
                    {'cource_ids': [(4, course_id) for course_id in record.course_approve_line_ids.course.ids]})
            else:
                self.env['class.class'].create({
                    'semester_id': record.semester_name_id.id,
                    'cource_ids': [(6, 0, record.course_approve_line_ids.course.ids)],
                    'relation_id': record.class_id.id,
                })

        self.status = 'approved'

    def action_course_reject(self):
        self.status = 'reject'

    def reset_to_draft(self):
        for rec in self:
            rec.status = 'draft'

    @api.onchange('school_department_id')
    def onchange_department(self):
        self.class_id = False
        self.semester_name_id = False

    def action_select(self):
        for line in self.course_approve_line_ids:
            line.is_tick = True

    @api.onchange('class_id', 'semester_name_id')
    def onchange_school_department_id(self):
        for rec in self:
            if rec.course_approve_line_ids:
                rec.course_approve_line_ids = False
            course = rec.env['assign.course'].search(
                [('class_id', '=', rec.class_id.id), ('semester_name_id', '=', rec.semester_name_id.id),
                 ('state', '=', 'approved')])
            if course:
                # rec.class_id = course.class_id.id
                for course_id in course:
                    # for line in course_id.course_subject_line_ids:
                    approve_course_line_id = self.env['approve.course.line'].search(
                        [('course_name_id', '=', rec.class_id.id),
                         ('semester', '=', rec.semester_name_id.id),
                         ('course', 'in', course_id.course_subject_id.ids)])
                    if not approve_course_line_id:
                        rec.update({
                            'course_approve_line_ids': [(0, 0, {
                                "course_name_id": rec.class_id.id,
                                "semester": rec.semester_name_id.id,
                                "course": course_id.course_subject_id.ids,
                            })],
                        })


class ApproveCourseLine(models.Model):
    _name = "approve.course.line"
    _description = "Assign Course line"

    is_tick = fields.Boolean(' ', tracking=True)
    course_name_id = fields.Many2one('class.room', string="Class Name", tracking=True)
    semester = fields.Many2one('semester.semester', string="Semester", tracking=True)
    course = fields.Many2many('school.subject', string="Subject Name", tracking=True)
    assign_course_id = fields.Many2one('approve.course', tracking=True)
