# -*- coding : utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    academic_year_id = fields.Many2one('academic.year', related="company_id.academic_year_id", readonly=False)
    examination_boolean = fields.Boolean('Examination Restriction')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update({
            'examination_boolean': self.env['ir.config_parameter'].sudo().get_param('examination_boolean', default=False),
        })
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('examination_boolean', self.examination_boolean)
