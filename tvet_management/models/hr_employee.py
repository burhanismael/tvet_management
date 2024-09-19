
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    sequence_no = fields.Char(string="Sequence No", copy=False, default='New')
    faculty_id = fields.Many2one('school.faculty')
    type_of_employee = fields.Selection([('normal_emp', 'Normal Employee'), ('lecturer', 'Lecturer')], string="Type Of Employee")
    is_lecturer = fields.Boolean(default=False)
    is_lecturer_check = fields.Boolean(default=False, compute='compute_lecturer')

    def compute_lecturer(self):
        for record in self:
            check_lecturer = self.env['create.lecturer'].search_count([('sequence_no', '=', self.sequence_no)])
            if check_lecturer:
                record.is_lecturer_check = True
            else:
                record.is_lecturer_check = False

    @api.model
    def create(self, vals):
        if vals.get('sequence_no', _('New')) == _('New'):
            vals['sequence_no'] = self.env['ir.sequence'].next_by_code('hr.employee') or _('New')
        res = super(HrEmployee, self).create(vals)
        return res

    def action_lecturer(self):
        result = {
            "type": "ir.actions.act_window",
            "res_model": "create.lecturer",
            "domain": [('sequence_no', '=', self.sequence_no)],
            "context": {"create": False},
            "name": _("Lecturer"),
            'view_mode': 'tree,form',
        }
        return result

    def btn_create_lecturer(self):
        result = {
                "type": "ir.actions.act_window",
                "res_model": "create.lecturer",
                "name": _("Create Lecturer"),
                'view_mode': 'form',
                "context": {
                    'default_sequence_no': self.sequence_no,
                    'default_name': self.name,
                    'default_mobile_number': self.mobile_phone,
                    'default_lecturer_photo': self.image_1920,
                    'default_dob': self.birthday,
                    'default_email': self.work_email,
                    'default_gender': self.gender,
                    'default_visa_details': self.visa_no,
                    'default_faculty_id': self.faculty_id.id,
                    # 'default_employee_type': self.type_of_employee,
                    # 'default_street_1': self.
                    # 'default_street_2': self.
                    # 'default_city': self.
                    # 'default_pin_code': self.
                    # 'default_state_id': self.
                    # 'default_country_id': self.
                    # 'default_qualification': self.
                    },
         }
        return result

    def name_get(self):
        result = []
        for rec in self:
            if rec.is_lecturer:
                name = str(rec.faculty_id.faculty_code)+str(rec.sequence_no) + '-' + str(rec.name)
                result.append((rec.id,name))
            else:
                name = str(rec.name)
                result.append((rec.id,name))
        return result

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    faculty_id = fields.Many2one('school.faculty')
    type_of_employee = fields.Selection([('normal_emp', 'Normal Employee'), ('lecturer', 'Lecturer')], string="Type Of Employee")
    is_lecturer = fields.Boolean(default=False)