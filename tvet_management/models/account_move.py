# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"
    
    is_student = fields.Boolean(default=False)
    admission_id = fields.Char('Admission ID')
    is_invoice_cron = fields.Boolean(default=False)
    active = fields.Boolean(default=True)
    student_type_product = fields.Char('Student Product Type', compute='get_type_student_product', store=True)
    student_department_name = fields.Char('Department name', compute='get_type_student_product', store=True)

    # def action_register_payment(self):
    #     res = super(AccountMove, self).action_register_payment()
    #     if 'context' in res and self.env.user.has_group('tvet_management.edit_can_edit_payment_access'):
    #         res['context']['default_payment_bool'] = False
    #     else:
    #         res['context']['default_payment_bool'] = True
    #     return res

    @api.depends('invoice_line_ids.product_id', 'partner_id')
    def get_type_student_product(self):
        for move in self:
            for rec in move.invoice_line_ids:
                move.student_type_product =  rec.product_id.name
            if move.partner_id:
                student_id = move.env['student.registration'].search([('student_name_id', '=', move.partner_id.id)], limit=1)
                move.student_department_name = student_id.department_id.name

    def action_account_update_department(self):
        for move in self:
            for rec in move.invoice_line_ids:
                move.student_type_product =  rec.product_id.name
            if move.partner_id:
                student_id = move.env['student.registration'].search([('student_name_id', '=', move.partner_id.id)], limit=1)
                move.student_department_name = student_id.department_id.name

    @api.depends('partner_id')
    def _compute_student(self):
        for move in self:
            student_id = self.env['student.registration'].search(
                [
                    ('student_name_id', '=', move.partner_id.id),
                ]
            )
            student_id = student_id[0] if len(student_id) > 1 else student_id
            for student in student_id:
                move.gender = student_id.gender
                move.nationality_id = student_id.nationality_id.id
                move.marital_status = student_id.marital_status
                move.graduate_year = student_id.graduate_year
                move.grade = student_id.grade
                move.parent_city = student_id.parent_city
                move.state_id = student_id.state_id.id
                move.country_id = student_id.country_id.id
                move.location = student_id.location.id
                move.scholarship_product_id = student_id.scholarship_product_id.id
                move.school_name = student_id.school_name
                move.occupation = student_id.occupation
                move.blood_group = student_id.blood_group
                move.academic_year_id = student_id.academic_year_id.id
                move.shift_id = student_id.shift_id.id
                move.faculty_id = student_id.faculty_id.id
                move.department_id = student_id.department_id.id
                move.classroom_id = student_id.classroom_id.id
                move.semester_id = student_id.semester_id.id
                move.student_type = student_id.student_type
                move.student_state = student_id.status

    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender",
                              compute='_compute_student', store=True)
    nationality_id = fields.Many2one('country.nationality', string="Nationality",
                                     compute='_compute_student', store=True)
    marital_status = fields.Selection([('married', 'Married'), ('unmarried', 'Unmarried')],
                                      string="Marital Status", compute='_compute_student',
                                      store=True)
    graduate_year = fields.Char("Graduate Year", compute='_compute_student', store=True)
    grade = fields.Char(string="Grade", compute='_compute_student', store=True)
    parent_city = fields.Char(string="Parent City", compute='_compute_student', store=True)
    state_id = fields.Many2one('res.country.state', string="Parent State",
                               domain="[('country_id','=?',country_id)]",
                               compute='_compute_student', store=True)
    country_id = fields.Many2one('res.country', string="Parent Country", compute='_compute_student',
                                 store=True)
    location = fields.Many2one('class.location', string="Location", compute='_compute_student',
                               store=True)

    scholarship_product_id = fields.Many2one('product.product',
                                             domain="[('is_scholarship', '=', True)]",
                                             compute='_compute_student',
                                             store=True)
    school_name = fields.Char(string="School Name", compute='_compute_student',
                              store=True)

    occupation = fields.Selection([('employed', 'Employed'), ('unemployed', 'Unemployed')],
                                  string="Occupation", compute='_compute_student',
                                  store=True)
    blood_group = fields.Selection(
        [('a+', 'A+'), ('a-', 'A-'), ('ab+', 'AB+'), ('ab-', 'AB-'), ('b+', 'B+'), ('b-', 'B-'),
         ('o+', 'O+'),
         ('o-', 'O-')], string="Blood Group", compute='_compute_student',
        store=True)

    academic_year_id = fields.Many2one('academic.year', string="Academic Year",
                                       compute='_compute_student',
                                       store=True)

    shift_id = fields.Many2one('school.shift', string="Shift", compute='_compute_student',
                               store=True)

    faculty_id = fields.Many2one('school.faculty', string="Faculty", compute='_compute_student',
                                 store=True)

    department_id = fields.Many2one('school.department', string="Department",
                                    compute='_compute_student',
                                    store=True)

    classroom_id = fields.Many2one('class.room', string="Class", compute='_compute_student',
                                   store=True)

    semester_id = fields.Many2one('semester.semester', string="Semester",
                                  domain="[('class_id', '=', classroom_id)]",
                                  compute='_compute_student',
                                  store=True)

    student_type = fields.Selection([('new', 'New'), ('transfer', 'Transfer')],
                                    compute='_compute_student',
                                    store=True)
    student_state = fields.Selection([('new', 'New'), ('enrolled', 'Enrolled'), ('drop_out', 'Drop Out'), ('inactive', 'Inactive'),
         ('graduated', 'Graduated')],
                                    compute='_compute_student',
                                    store=True)

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.admission_id and self.state == 'posted':
            check_status = self.env['student.admission'].search([('admission_id', '=', self.admission_id)])
            check_status.status = 'inprogress'
            check_status.payment_status = 'posted'
        return res
    
    @api.model
    def create(self,vals):
        res = super(AccountMove, self).create(vals)
        if res.is_student and not res.is_invoice_cron:
            student_status = self.env['student.admission'].search([('admission_id', '=', res.admission_id)], limit=1)
            student_status.status = 'finance'
            # student_faculty_id = self.env['student.registration'].search([('admission_id', '=', res.admission_id)], limit=1)
            # product_id = self.env['product.product'].search([('faculty_id', '=', student_faculty_id.faculty_id.id),('is_admission_product', '=', True)])
            # if product_id:
            #     for product in product_id:
            #         res.update({
            #                 'invoice_line_ids': [(0, 0, {
            #                     'product_id' : product.id,
            #                     'price_unit' : product.fee_amount,
            #                     })],
            #                 })
        return res

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    active = fields.Boolean(default=True)

class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    active = fields.Boolean(default=True)

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    active = fields.Boolean(default=True)
