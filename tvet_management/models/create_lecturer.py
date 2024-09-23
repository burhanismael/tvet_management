# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class CreateLecturer(models.Model):
    _name = "create.lecturer"
    _rec_name = 'name'
    _description = "Lecturer Information"
    _inherit = ['mail.thread', 'mail.activity.mixin']
   
    sequence_no = fields.Char(string="Sequence No", tracking=True)
    name = fields.Char(string="Name", tracking=True)
    user_id = fields.Many2one('res.users', tracking=True)
    lecturer_photo = fields.Binary(string="Photo", tracking=True)
    dob = fields.Date(string="Date of Birth", tracking=True)
    mobile_number = fields.Char("Mobile", tracking=True)
    email = fields.Char(string="Email", tracking=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender", tracking=True)
    allocated_department = fields.Char(string="Allocated Department", tracking=True)
    address = fields.Char(string="Address", tracking=True)
    street_1 = fields.Char(string="Street1", tracking=True)
    street_2 = fields.Char(string="Street2", tracking=True)
    city = fields.Char(string="City", tracking=True)
    pin_code = fields.Char(string="Pin Code", tracking=True)
    state = fields.Char(string="State", tracking=True)
    state_id = fields.Many2one('res.country.state', string="Parent State", domain="[('country_id','=?',country_id)]", tracking=True)
    blood_group = fields.Selection([('a+','A+'),('a-','A-'),('ab+','AB+'),('ab-','AB-'),('b+','B+'),('b-','B-'),('o+','O+'),('o-','O-')], string="Blood Group", tracking=True)
    visa_details = fields.Char(string="Visa Details", tracking=True)
    country_id = fields.Many2one('res.country', string="Parent Country", tracking=True)
    qualification = fields.Selection([('undergraduate','Undergraduate'),('post_graduate','Post-graduate')], string="Qualification", tracking=True)
    employee_type = fields.Selection([('normal_emp', 'Normal Employee'), ('lecturer', 'Lecturer')], string="Employee type", tracking=True)
    qualification_ids=fields.One2many('create.lecturer.qualification','qualification_id', tracking=True)
    is_assign_lecturer = fields.Boolean(default=False, tracking=True)
    faculty_id = fields.Many2one('school.faculty', tracking=True)

    def action_create_user(self):
        vals = {
            'name' : self.name,
            'login' : self.email,
            'mobile' : self.mobile_number
            }
        user_id = self.env['res.users'].create(vals)
        self.user_id = user_id.id
        check_seq = self.env['hr.employee'].search([('sequence_no','=', self.sequence_no)], limit=1)
        check_seq.user_id = user_id.id

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

    def name_get(self):
        result = []
        for rec in self:
            name = str(rec.name)
            result.append((rec.id,name))
        return result
        
class CreateLecturerQualification(models.Model):
    _name = "create.lecturer.qualification"
    _description = "Qualification Information" 

    degree = fields.Char(string="Degree", tracking=True)
    specialization = fields.Char(string="Specialization", tracking=True)
    year = fields.Char(string="Year", tracking=True)
    institute = fields.Char(string="Institute", tracking=True)
    qualification_id = fields.Many2one('create.lecturer',string="Qualification Id", tracking=True)
