# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ClassRoom(models.Model):
    _name = "class.room"
    _rec_name = "name"
    _description = "Class Room Information"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Class Name", store=True, tracking=True)
    course_id = fields.Many2one('course.subject', string="Course Name", tracking=True)
    cource_ids = fields.Many2many('course.subject', string="Course", tracking=True)
    class_year = fields.Char(string="Class Year", tracking=True)
    academic_year_id = fields.Many2one('academic.year', string="Class Year", tracking=True)
    shift_id = fields.Many2one('school.shift', string="Shift", tracking=True)
    school_department_id = fields.Many2one('school.department', string="Department Name", tracking=True)
    semester_id = fields.Many2one('semester.semester', string="Current Semester")
    class_room_ids = fields.One2many('class.class', 'relation_id', string="class name")


    @api.constrains('name', 'school_department_id')
    def _check_duplicate(self):
        if self.name and self.school_department_id:
            class_room_id = self.env['class.room'].search(
                [
                    ('name', '=', self.name),
                    ('school_department_id', '=', self.school_department_id.id),
                    ('semester_id', '=', self.semester_id.id)
                ]
            )
            if len(class_room_id) > 1:
                raise ValidationError(_('Already available'))



class classOnetomany(models.Model):
    _name = "class.class"

    relation_id = fields.Many2one('class.room', string="class Room name")
    relation_name = fields.Char(related='relation_id.name', store=True)
    # name = fields.Char('Class Name')
    semester_id = fields.Many2one('semester.semester', string="Semester")
    cource_ids = fields.Many2many('school.subject', string="Subject", tracking=True)
