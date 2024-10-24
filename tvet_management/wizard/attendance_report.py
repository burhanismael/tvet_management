# -*- coding: utf-8 -*-

import base64
import io
from collections import defaultdict
from datetime import datetime

import pytz
import xlwt, xlsxwriter
from odoo import fields, models, api
from PIL import Image


class AttendanceReportView(models.TransientModel):
    _name = "attendance.report"

    date = fields.Date('Date From', required="1")
    data = fields.Binary(string="Data")
    name = fields.Char(string="name")
    date_to = fields.Date('Date To', required="1")
    department_name = fields.Many2one('school.department', string='Department Name')
    class_name = fields.Many2one('class.room', string="Batch Name", required="1")
    sem = fields.Many2one('semester.semester', domain="[('class_id', '=', class_name)]", string="Tier", required="1")
    cource_ids = fields.Many2many('course.subject', string="Subject")

    @api.onchange('class_name', 'department_name')
    def onchange_class_id(self):
        for rec in self:
            semester_id = self.env['semester.semester'].search([('class_id', '=', rec.class_name.id)])
            rec.sem = semester_id.ids

    def get_student_ids(self, class_id):
        return self.env['student.registration'].search([('classroom_id', '=', class_id.id), ('status', '=', 'enrolled')])

#    @api.onchange('class_name')
#    def class_based_domain(self):
#        if self.class_name:
#            semister_ids = self.class_name.class_room_ids.mapped('semester_id')
#            domain = [('id', 'in', semister_ids.ids)]
#            return {'domain': {'sem': domain}}


#    @api.onchange('sem')
#    def semseter_based_course_domain(self):
#        if self.sem:
#            cource_ids = self.class_name.class_room_ids.filtered(lambda x:x.semester_id.id == self.sem.id).mapped('cource_ids')
#            domain = [('id', 'in', cource_ids.ids)]
#            return {'domain': {'cource_ids': domain}}


#    @api.onchange('cource_ids')
#    def semseter_course_domain(self):
#        if self.sem:
#            cource_ids = self.class_name.class_room_ids.filtered(lambda x:x.semester_id.id == self.sem.id).mapped('cource_ids')
#            domain = [('id', 'in', cource_ids.ids)]
#            return {'domain': {'cource_ids': domain}}


    def excle_download_action(self):
        data = {
               'date':self.date,
               'date_to':self.date_to,
               'school_department_id': self.department_name.id if self.department_name else False ,
               'class_id': self.class_name.id if self.class_name else False,
               'semester_id': self.sem.id if self.sem else False,
               'cource_ids': self.cource_ids.ids
        }
        return self.env.ref('tvet_management.attendanace_data_xlsx').report_action(self, data=data)

    def pdf_download_action(self):
        data = {
               'date':self.date,
               'date_to':self.date_to,
               'school_department_id': self.department_name.id if self.department_name else False ,
               'class_id': self.class_name.id if self.class_name else False,
               'semester_id': self.sem.id if self.sem else False,
               'cource_ids': self.cource_ids.ids
        }
        return self.env.ref('tvet_management.attendanace_data_pdf').report_action(self, data=data)
