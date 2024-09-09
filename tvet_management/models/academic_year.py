# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, date


class AcademicYear(models.Model):
    _name = "academic.year"
    _rec_name = 'name'
    _description = "Academic Year Information"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Academic Year", tracking=True)
    start_date = fields.Date(string="Start Date", tracking=True)
    end_date = fields.Date(string="End Date", tracking=True)

    @api.model
    def create(self, vals):
        res = super(AcademicYear, self).create(vals)
        if res['name'] == False or len(res['name']) != 9 or res['name'][4] != '-':
            raise ValidationError("Please enter valid academic year format")
        return res

    @api.onchange('start_date', 'end_date')
    def _onchange_academic_year(self):
        if self.start_date and self.end_date:
            self.name = str(self.start_date.year) + "-" + str(self.end_date.year)

    @api.constrains('name')
    def _check_duplicate(self):
        if self.name:
            academic_year_id = self.env['academic.year'].search(
                [
                    ('name', '=', self.name)
                ]
            )
            if len(academic_year_id) > 1:
                raise ValidationError(_('Academic year already available'))
