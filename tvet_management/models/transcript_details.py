# -- coding: utf-8 --
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, _

class TranscriptDetails(models.Model):
    _name = "transcript.details"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Html(string="Details")
    award_class_ids = fields.One2many('cgpa.transcript', 'relation_id', string="Award class")
    mark_class_ids = fields.One2many('mark.transcript', 'relation_id', string="Award class")


class Cgps(models.Model):
    _name = "cgpa.transcript"
    relation_id = fields.Many2one('transcript.details', string="relation")
    from_a = fields.Char('Cgpa From')
    from_t = fields.Char('Cgpa To')
    achivment = fields.Char('Achievement')
    class_name = fields.Char('Batch')

class MarkGreadPay(models.Model):
    _name = "mark.transcript"
    relation_id = fields.Many2one('transcript.details', string="relation")
    marks = fields.Char('Marks')
    grade = fields.Char('Grade')
    point = fields.Char('Point')





