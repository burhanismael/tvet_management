# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ManageTimetable(models.Model):
    _name = "manage.timetable"
    _rec_name = 'school_department_id'
    _description = "Manage Timetable Information"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_day(self):
        return str(fields.Date.today().weekday())

   
    school_department_id = fields.Many2one('school.department', string="Department Name", tracking=True)
    class_id = fields.Many2one('class.room', string="Class Name", domain="[('school_department_id', '=', school_department_id)]", tracking=True)
    semester_id = fields.Many2one('school.semester', tracking=True)
    course_id = fields.Many2many('school.course', string="Course Name", tracking=True)
    day = fields.Selection([('0', 'Monday'),
                            ('1', 'Tuesday'),
                            ('2', 'Wednesday'),
                            ('3', 'Thursday'),
                            ('4', 'Friday'),
                            ('5', 'Saturday'),
                            ('6', 'Sunday')
                            ], string="Day", default=_get_default_day, tracking=True)
    location = fields.Many2one('class.location', string="Location", tracking=True)
    start_time = fields.Float(string="Start Time", tracking=True)
    end_time = fields.Float(string="End Time", tracking=True)
    break_start_time = fields.Float(string="Start Time", tracking=True)
    break_end_time = fields.Float(string="End Time", tracking=True)
    time_table_date = fields.Datetime(string="Time Table Date", default=lambda self: fields.Datetime.now(), tracking=True)

    @api.constrains('school_department_id', 'class_id', 'semester_id', 'course_id', 'day', 'location', 'start_time', 'end_time')
    def _check_duplicate(self):
        timetable_id = self.env['manage.timetable'].search([
                                        ('school_department_id', '=', self.school_department_id.id),
                                        ('class_id', '=', self.class_id.id),
                                        ('semester_id', '=', self.semester_id.id),

                                        ('day', '=', self.day),
                                        ('location', '=', self.location.id),
                                        ('start_time', '=', self.start_time),
                                        ('end_time', '=', self.end_time),
                                        ])
        if len(timetable_id) > 1:
            raise ValidationError(_('Already Available!'))

    @api.constrains('location', 'time_table_date', 'start_time', 'end_time', 'day')
    def _check_duplicate_time_record(self):
        exam_date = self.time_table_date.date()
        timetable_ids = self.env['manage.timetable'].search([
            ('day', '=', self.day),
            ('location', '=', self.location.id),
            '|',
            '&', ('start_time', '<=', self.start_time), ('end_time', '>=', self.start_time),
            '&', ('start_time', '<=', self.end_time), ('end_time', '>=', self.end_time)
        ])
        table_ids = timetable_ids.filtered(lambda x:x.time_table_date.date() == exam_date)
        if len(table_ids) > 1:
            raise ValidationError(_('This room is scheduled for another course within this timeslot'))


    # @api.onchange('class_id')
    # def domain_semsseter_data(self):
    #     if self.class_id:
    #         approved_cource_ids = self.env['approve.course'].search([('class_id', '=', self.class_id.id), ('status', '=', 'approved')])
    #         domain = [('id', 'in', approved_cource_ids.mapped('semester_name_id').ids)]
    #         return {'domain': {'semester_id': domain}}


    # @api.onchange('semester_id')
    # def sem_based_domain(self):
    #     if self.semester_id:
    #         rooms_ids = self.class_id.class_room_ids.filtered(lambda x: x.semester_id.semester_name == self.semester_id.semester_name)
    #         course_ids = rooms_ids.mapped('cource_ids')
    #         domain = [('id', 'in', course_ids.ids)]
    #         return {'domain': {'course_id': domain}}