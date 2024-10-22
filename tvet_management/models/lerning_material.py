# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LerningMaterials(models.Model):
    _name = "learning.material"
    _rec_name = 'name'
    _description = "Lerning material Information"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", tracking=True)
    department_id = fields.Many2one('school.department', string="Department")
    type_of_material_id = fields.Many2one('type.material', string="Type of the materials")
    lerning_name = fields.Char(string="Name")
    attechment = fields.Binary(string="Attechment")

    @api.model
    def create(self, vals):
        code = self.env['ir.sequence'].next_by_code('learning.material')
        vals['name'] = code
        learning_id = super(LerningMaterials, self).create(vals)

        return learning_id


class TypeOfMaterial(models.Model):
    _name = "type.material"
    _rec_name = 'name'
    _description = "Lerning material Information"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')