# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AssignSemester(models.Model):
    _name = "assign.semester"
    _rec_name = 'class_id'
    _description = "Assign semester"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # school_department_id = fields.Many2one('school.department', string="Department Name")
    class_id = fields.Many2one('class.room', string="Batch Name", tracking=True)
    academic_year_id = fields.Many2one('academic.year',string="Academic Year", tracking=True)
    semester_id = fields.Many2one('semester.semester', string="Tier Name", domain="[('class_id', '=', class_id)]", tracking=True)
    remarks = fields.Text(string="Remarks", tracking=True)
    status = fields.Selection([('draft','Draft'),('approved','Semester Assign'),('invoice','Invoice Created')], default="draft", copy=False, tracking=True)
    date_invoice = fields.Date(string=" Invoice Date", required=True)
    student_ids = fields.Many2many('student.registration', string="Student", tracking=True)
    invoice_ids = fields.Many2many('account.move', copy=False, tracking=True)
    invoice_count = fields.Integer(string='Invoice Count', compute='_compute_invoice_count', tracking=True)
    analitic_account_id = fields.Many2one('account.analytic.account', string="Analytic account")

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.invoice_ids)

    @api.onchange('class_id')
    def onchange_semester(self):
        if self.class_id:
            assign_semester = self.env['student.registration'].search([('status', '=', 'enrolled'),
                                                                       ('classroom_id', '=', self.class_id.id),
                                                                       ('is_alumni', '=', False)])
            if assign_semester:
                assign_semester_ids = []
                for semester in assign_semester:
                    assign_semester_ids += semester.ids
                self.student_ids = assign_semester_ids
            else:
                self.student_ids = False
        else:
            self.student_ids = False

    def action_semester(self):
        assign_semester = self.env['student.registration'].search([('status', '=', 'enrolled'),
                                                                   ('classroom_id', '=', self.class_id.id),
                                                                   ('is_alumni', '=', False)])
        self.class_id.semester_id = self.semester_id.id
        if assign_semester:
            self.status = 'approved'
            for semester in assign_semester:
                semester.semester_id = self.semester_id.id
                semester.academic_year_id = self.academic_year_id.id
        if not assign_semester:
            notification =  {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Information!'),
                    'message': 'Cannot find any data right now. Please try again later!',
                    'sticky': False,
                    }
                }
            return notification

    def action_open_invoice(self):
        result = {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "domain": [('id', 'in', self.invoice_ids.ids)],
            "context": {"create": False},
            "name": _("Semester Invoices"),
            'view_mode': 'tree,form',
        }
        return result

    def semester_invoice(self):
        list_invoice_ids = []
        for rec in self.student_ids:
            product_id = self.env['product.product'].search([('name', 'ilike', 'Tuition'), ('is_fee_product', '=', True)], limit=1)
            if not product_id:
                raise ValidationError("Semester Fee Type Is Not Created")

            product_lines = []

            price_schedule_id = self.env['price.schedule'].search([('department_id', '=', rec.department_id.id),
                                                                   ('description_id', '=', product_id.id),
                                                                   ('class_id', '=', rec.classroom_id.id)
                                                                   ])
            if not price_schedule_id:
                raise ValidationError("%s's Price Schedule Is Not Created" % rec.department_id.name)

            price = price_schedule_id.fee
            scholarship = 0
            if rec.scholarship_product_id:
                if rec.scholarship_product_id.scholarship_type == 'fixed':
                    scholarship = rec.scholarship_product_id.scholarship_fixed
                if rec.scholarship_product_id.scholarship_type == 'percentage':
                    scholarship = (price * rec.scholarship_product_id.scholarship_per) / 100

            if scholarship > 0:
                product_lines.append((0, 0, {
                    'product_id': price_schedule_id.description_id.id,
                    'analytic_account_id': self.analitic_account_id.id,
                    'price_unit': price_schedule_id.fee - scholarship,
                    'name': price_schedule_id.description_id.name
                }))
            else:
                product_lines.append((0, 0, {
                    'product_id': price_schedule_id.description_id.id,
                    'analytic_account_id': self.analitic_account_id.id,
                    'price_unit': price_schedule_id.fee,
                    'name': price_schedule_id.description_id.name
                }))

            vals = {
                'move_type': 'out_invoice',
                'invoice_date': self.date_invoice,
                'admission_id': rec.admission_id + 'SEM',
                'is_student': 1,
                'partner_id': rec.student_name_id.id,
                'invoice_line_ids': product_lines
            }
            move_id = self.env['account.move'].create(vals)
            list_invoice_ids.append(move_id.id)
            rec.is_semester_invoice = True
            self.status = 'invoice'
        self.invoice_ids = [(6, 0,list_invoice_ids)]
