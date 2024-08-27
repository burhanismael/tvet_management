from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TvetProjects(models.Model):
    _name = "tvet.project"
    _rec_name = "project_name"
    _description = "TVET Projects"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    project_name = fields.Char(string="Project Name", tracking=True)
    project_code = fields.Char(string="Project Code", tracking=True)
    donor = fields.Char(string="Donor", tracking=True)
