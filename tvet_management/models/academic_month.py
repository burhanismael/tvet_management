# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AcademicMonth(models.Model):
    _name = "academic.month"
    _rec_name = 'name'
    _description = "Academic Month Information"

    name = fields.Char(string="Academic Month")