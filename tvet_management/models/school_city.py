# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SchoolCity(models.Model):
    _name = "school.city"
    _rec_name = 'name'
    _description = "City"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Subject", tracking=True)



