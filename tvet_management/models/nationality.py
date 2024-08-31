# -*- coding: utf-8 -*-
from odoo import api, fields, models

class CountryNationality(models.Model):
    _name = "country.nationality"
    _rec_name = 'name'
    _description = "NationalityInformation"

    name = fields.Char(string="Nationality")