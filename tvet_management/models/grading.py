# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Grading(models.Model):
    _name = "grading.policy"

    minimum = fields.Float('Minimum Result')
    maximum = fields.Float('Maximum Result')
    grade = fields.Char('Grade')
    gpa = fields.Char('GPA')
    decision = fields.Char('Decision')
    is_medical = fields.Boolean(string="Medicine")

class HealthGrading(models.Model):
    _name = "health.grading.policy"

    minimum = fields.Float('Minimum Result')
    maximum = fields.Float('Maximum Result')
    grade = fields.Char('Grade')
    gpa = fields.Char('GPA')
    decision = fields.Char('Decision')
