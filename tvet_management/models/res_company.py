# -*- coding : utf-8 -*-

from odoo import models, fields, api

class res_company(models.Model):
	_inherit = 'res.company'


	academic_year_id = fields.Many2one('academic.year')

	at_dance = fields.Char('Attendance %')
	student_card_sign = fields.Binary('Student Card Back ')
	uni_header = fields.Binary('Student Header')
