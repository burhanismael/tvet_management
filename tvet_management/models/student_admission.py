# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class StudentAdmission(models.Model):
    _name = "student.admission"
    _rec_name = 'admission_id'
    _description = "Admission Information"
    _inherit = ['mail.thread', 'mail.activity.mixin']
   
    admission_id = fields.Char(string="Admission ID", tracking=True)
    student_id = fields.Char(string="Student ID", tracking=True)
    student_name_id = fields.Many2one("res.partner", string="Student", domain="[('is_student','=',True)]", tracking=True)
    student_type = fields.Selection([('new','New'),('transfer','Transfer')], string="Student Type", tracking=True)
    registration_type = fields.Selection([('undergraduate','Undergraduate'),('post_graduate','Post-graduate')], string="Registration Type", tracking=True)
    payment_status = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ], string="Payment Status", readonly=True, default='draft', tracking=True)
    contact = fields.Char(string="Contact", tracking=True)
    parent_contact = fields.Char(string="Parent Contact", tracking=True)
    student_photo = fields.Binary(string="Passport Size Photo", tracking=True)
    secondary_certificate = fields.Binary(string="Secondary Certificate", tracking=True)
    # admission_fee = fields.Binary(string="Admission Fee")
    blood_group = fields.Selection([('a+','A+'),('a-','A-'),('ab+','AB+'),('ab-','AB-'),('b+','B+'),('b-','B-'),('o+','O+'),('o-','O-')], string="Blood Group", tracking=True)
    blood_group_certificate = fields.Binary(string="Blood Group Certificate", tracking=True)
    transcript = fields.Binary(string="Transcript", tracking=True)
    testimonial = fields.Binary(string="Testimonial of the Previous University attended", tracking=True)
    degree_certificate = fields.Binary(string="Bachelor’s degree Certificate", tracking=True)
    identification_card = fields.Binary(string="Passport or Identification Card", tracking=True)
    is_free = fields.Boolean(default=False, tracking=True)
    html_free = fields.Html(compute="_compute_html_free", tracking=True)
    status = fields.Selection([('draft','Draft'),('finance','Finance'),('inprogress','In Progress'),('done','Done')], default='draft', tracking=True)
    invoice_count = fields.Integer(compute='compute_count', tracking=True)
    color = fields.Selection([('red', 'Red'), ('green', 'Green'), ('blue', 'Blue')], string='Color')

    @api.onchange('student_photo')
    def _onchange_student_photo(self):
        # Find related student registration records and update the image field
        related_registrations = self.env['student.registration'].search([('admission_id', '=', self.admission_id)])
        for registration in related_registrations:
            registration.image = self.student_photo

    @api.onchange('blood_group')
    def update_registration_blood_group(self):
        if self.admission_id:
            registrations = self.env['student.registration'].search([('admission_id', '=', self.admission_id)])
            registrations.write({'blood_group': self.blood_group})

    
    def _compute_html_free(self):
        for rec in self:
            if rec.is_free:
                rec.html_free = "<h2 style='color: red'>Free</h2>"
            else:
                rec.html_free = "<h2></h2>"

    def action_invoice(self):
        result = {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "domain": [('admission_id', '=', self.admission_id)],
            "context": {"create": False},
            "name": _("Invoices"),
            'view_mode': 'tree,form',
        }
        return result

    def action_free(self):
        for rec in self:
            rec.is_free = True
            rec.status = 'done'
            rec.change_status()

    def action_paid(self):
        self.is_free = False

    def change_status(self):
        if self.status == 'done':
            check_status = self.env['student.registration'].search([('admission_id', '=', self.admission_id)])
            for record in check_status:
                if record.status != 'enrolled':
                    record.status = 'enrolled'

    def get_invoice(self):
        # return {
        #     "type": "ir.actions.act_window",
        #     "view_mode": "form",
        #     "res_model": "account.move",
        #     "name": "Invoices",
        #     "domain":[('move_type', '=', 'out_invoice')],
        #     "context": {
        #         'default_move_type': 'out_invoice',
        #         'default_admission_id': self.admission_id,
        #         'default_is_student': 1,
        #         'default_partner_id': self.student_name_id.id,
        #         },
        #     }
        for rec in self:
            student_faculty_id = self.env['student.registration'].search([('admission_id', '=', rec.admission_id)], limit=1)
            product_id = self.env['product.product'].search([('faculty_id', '=', student_faculty_id.faculty_id.id),('is_admission_product', '=', True)])
            if not product_id:
                raise ValidationError("%s's fee is not created" % student_faculty_id.faculty_id.name)
            product_lines = []
            for line in product_id:
                product_lines.append((0, 0, {
                                'product_id' : line.id,
                                'price_unit' : line.fee_amount,
                            }))
            vals = {
                'move_type': 'out_invoice',
                'admission_id': rec.admission_id,
                'is_student': 1,
                'partner_id': rec.student_name_id.id,
                'invoice_line_ids': product_lines
            }
            account_move_id = self.env['account.move'].create(vals)
            return {
                'type': 'ir.actions.act_window',
                'name': 'My Action Name',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': account_move_id.id,
                'target': 'current',
            }

    def compute_count(self):
        for record in self:
            invoice = self.env['account.move'].search_count([('admission_id', '=', self.admission_id)])
            record.invoice_count = invoice

    def write(self, vals):
        res = super(StudentAdmission, self).write(vals)
        if self.status == 'inprogress' and self.secondary_certificate and self.blood_group_certificate and self.student_photo and self.registration_type == 'undergraduate':
            self.status = 'done'
            student_id = self.env['student.registration'].search([('admission_id', '=', self.admission_id)],limit=1)
            student_id.status = 'enrolled'
        elif self.status == 'done' and self.registration_type == 'undergraduate':
            if not self.secondary_certificate or not self.blood_group_certificate or not self.student_photo:
                self.status = 'inprogress'
                student_id = self.env['student.registration'].search([('admission_id', '=', self.admission_id)], limit=1)
                student_id.status = 'new'



        elif self.status == 'inprogress' and self.degree_certificate and self.identification_card  and self.student_photo and self.registration_type == 'post_graduate':
            self.status = 'done'
            student_id = self.env['student.registration'].search([('admission_id', '=', self.admission_id)],limit=1)
            student_id.status = 'enrolled'
        elif self.status == 'done' and self.registration_type == 'post_graduate':
            if not self.degree_certificate or not self.identification_card or not self.student_photo:
                self.status = 'inprogress'
                student_id = self.env['student.registration'].search([('admission_id', '=', self.admission_id)], limit=1)
                student_id.status = 'new'
        return res
