from odoo import api, fields, models, _


class AwardingSystem(models.Model):
    _name = "awarding.system"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Achievements', tracking=True)
    award = fields.Char('Award', tracking=True)
    m_cgpa = fields.Float('Maximum CGPA', tracking=True)
    cgpa = fields.Float('Minimum CGPA', tracking=True)
    is_madical = fields.Boolean('Medicine', tracking=True)
