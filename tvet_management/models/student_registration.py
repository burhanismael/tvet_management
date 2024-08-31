# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StudentRegistration(models.Model):
    _name = "student.registration"
    _description = "Student registration Information"
    _rec_name = 'student_name_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    admission_id = fields.Char(string="Admission ID", default=lambda self: _('New'), tracking=True)
    birth_place_id = fields.Many2one('school.city', string="Place of Birth", tracking=True)
    student_contact = fields.Char(string="Student Contact", required=True, tracking=True)
    education_level = fields.Selection([('intermediate', 'Intermediate'), ('secondary', 'Secondary'),
                                        ('diploma', 'Diploma'), ('degree', 'Degree')])
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender", tracking=True)
    parent_contact = fields.Char(string="Parent contact", required=True, tracking=True)
    intake_type = fields.Selection([('normal', 'Normal Intake'), ('recommended', 'Recommended Intake')],
                                   string="Intake Type", tracking=True)
    status = fields.Selection([('new', 'New'), ('enrolled', 'Enrolled'), ('drop_out', 'Drop Out'), ('inactive', 'Inactive'),
                            ('graduated', 'Graduated')], default="new", tracking=True)
    shift_id = fields.Many2one('school.shift', string="Shift", required=True, tracking=True)
    faculty_id = fields.Many2one('school.faculty', string="Faculty", tracking=True)
    department_id = fields.Many2one('school.department', string="Department", tracking=True)
    classroom_id = fields.Many2one('class.room', string="Class", tracking=True)
    semester_id = fields.Many2one('school.semester', string="Semester", domain="[('class_id', '=', classroom_id)]",
                                  tracking=True)
    dob = fields.Date(string="DOB", tracking=True)
    school_name = fields.Char(string="School Name", tracking=True)
    graduate_year = fields.Char("Graduate Year", tracking=True)
    roll_number = fields.Char(string="Roll Number", required=True, tracking=True)
    grade = fields.Char(string="Grade", tracking=True)




    occupation = fields.Selection([('employed', 'Employed'), ('unemployed', 'Unemployed')], string="Occupation", tracking=True)
    blood_group = fields.Selection(
        [('a+', 'A+'), ('a-', 'A-'), ('ab+', 'AB+'), ('ab-', 'AB-'), ('b+', 'B+'), ('b-', 'B-'), ('o+', 'O+'),
         ('o-', 'O-')], string="Blood Group", required=True, tracking=True)
    academic_year_id = fields.Many2one('academic.year', string="Academic Year", tracking=True)
    academic_month = fields.Selection(
        [('january', 'January'), ('february', 'February'), ('march', 'March'), ('april', 'April'), ('may-', 'May'),
         ('june', 'June'), ('july', 'July'), ('august', 'August'), ('september', 'September'), ('october', 'October'),
         ('november', 'November'), ('december', 'December')], string="Intake", required=True, tracking=True)

    student_type = fields.Selection([('new', 'New'), ('transfer', 'Transfer')], tracking=True)
    relationship_id = fields.Many2one('student.relationship', string="Relationship", tracking=True)


    stream = fields.Selection([('science', 'Science'), ('arts', 'Arts')], string="Stream", tracking=True)
    student_id = fields.Char(string="Student ID", tracking=True, copy=False)
    student_name_id = fields.Many2one('res.partner', string="Student Name", tracking=True)
    is_admitission_button_show = fields.Boolean(default=False, tracking=True)

    nationality_id = fields.Many2one('country.nationality', string="Nationality", tracking=True)
    email = fields.Char(string="Email", tracking=True)
    address = fields.Char(string="Address", tracking=True)
    marital_status = fields.Selection([('married', 'Married'), ('unmarried', 'Unmarried')], string="Marital Status", tracking=True)


    parent_name = fields.Char(string="Parent Name", tracking=True)
    parent_street_1 = fields.Char(string="Parent Street1", tracking=True)
    parent_street_2 = fields.Char(string="Parent Street2", tracking=True)
    parent_city = fields.Char(string="Parent City", tracking=True)
    state_id = fields.Many2one('res.country.state', string="Parent State", domain="[('country_id','=?',country_id)]", tracking=True)
    country_id = fields.Many2one('res.country', string="Parent Country", tracking=True)
    student_balance = fields.Integer(string="Student Balance", tracking=True)
    is_alumni = fields.Boolean(default=False, tracking=True)
    location = fields.Many2one('class.location', string="Location", tracking=True)
    is_semester_invoice = fields.Boolean(tracking=True)
    course_subject_id = fields.Many2many('school.course', string='Course', tracking=True)
    student_id_issue_date = fields.Date('Student ID Issue Date', tracking=True)
    student_id_expired_date = fields.Date('Student ID Expired Date', tracking=True)
    is_user = fields.Boolean(string="Is User Create", tracking=True)
    student_user_id = fields.Many2one('res.users', string="student User Id", tracking=True)
    mothers_name = fields.Char(string="Mother's Name", required=True)
    color = fields.Selection([('red', 'Red'), ('green', 'Green'), ('blue', 'Blue')], string='Color')


    @api.constrains('student_id')
    def check_student_id_dublicate(self):
        if self.student_id:
            student_ids = self.env['student.registration'].search([('student_id', '=', self.student_id)])
            if len(student_ids) > 1:
                raise ValidationError(_('Student Id is already available'))

    @api.onchange('blood_group')
    def update_admission_blood_group(self):
        if self.admission_id:
            registrations = self.env['student.admission'].search([('admission_id', '=', self.admission_id)])
            registrations.write({'blood_group': self.blood_group})
    

    def check_secondary_certificate(self):
        if self.admission_id:
            admission = self.env['student.admission'].search([('admission_id','=',self.admission_id)])
            if admission and admission.secondary_certificate:
                return "True"
            else:
                return "False"

    def check_blood_certificate(self):
        if self.admission_id:
            admission = self.env['student.admission'].search([('admission_id','=',self.admission_id)])
            if admission and admission.blood_group_certificate:
                return "True"
            else:
                return "False"

    def _compute_image(self):
        for rec in self:
            if rec.admission_id:
                admission_id = self.env['student.admission'].search([('admission_id', '=', rec.admission_id)])
                rec.admission_id_id = admission_id.id

    admission_id_id = fields.Many2one('student.admission', store=False)
    image = fields.Binary(string="Student Photo", store=True)

    @api.constrains('email', 'student_contact')
    def _check_duplicate(self):

        if self.email:
            student_ida = self.env['student.registration'].search(
                [
                    ('email', '=', self.email)
                ]
            )

            if len(student_ida) > 1:
                raise ValidationError(_('Email is already available'))

        if self.student_contact:
            student_idsq = self.env['student.registration'].search(
                [
                    ('student_contact', '=', self.student_contact)
                ]
            )
            if len(student_idsq) > 1:
                raise ValidationError(_('Student Contact is already available'))

    def student_invoice(self):
        result = {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "domain": [('admission_id', '=', self.admission_id + 'SEM')],
            "context": {"create": False},
            "name": _("Invoices"),
            'view_mode': 'tree,form',
        }
        return result

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

    @api.model
    def create(self, vals):
        vals['status'] = 'new'
        if vals.get('admission_id', _('New')) == _('New'):
            vals['admission_id'] = self.env['ir.sequence'].next_by_code('student.registration') or _('New')
        res = super(StudentRegistration, self).create(vals)
        return res

    def student_admission_start(self):
        self.is_admitission_button_show = True
        vals = {
            'student_name_id': self.student_name_id.id,
            'parent_contact': self.parent_contact,
            'contact': self.student_contact,
            'student_id': self.student_id if self.student_id else "",
            'intake_type': self.intake_type,
            'admission_id': self.admission_id,
        }
        return self.env['student.admission'].create(vals)

    def student_record(self):
        result = {
            "type": "ir.actions.act_window",
            "res_model": "student.admission",
            "domain": [('admission_id', '=', self.admission_id)],
            "context": {"create": False},
            "name": _("Student Admission"),
            'view_mode': 'tree,form',
        }
        return result

    def _invoice_cron_action(self):
        print("************************")
        # student_registration_ids = self.env['student.registration'].search([])
        # for student_registration in student_registration_ids:
        #     replacement = "UOBG"
        #     text = student_registration.admission_id
        #     student_registration.admission_id = text.replace(text[0:6], replacement, 1)
        # current_academic_year = self.env['res.config.settings'].search([], limit=1)
        # if not current_academic_year.academic_year_id:
        #     raise ValidationError("Please select academic year")
        # enrolles_student = self.search([('status', '=', 'enrolled'),('academic_year_id', '=', current_academic_year.academic_year_id.id)])
        # for rec in enrolles_student:
        #     vals = {
        #         'move_type': 'out_invoice',
        #         'admission_id': rec.admission_id,
        #         'is_student': 1,
        #         'partner_id': rec.student_name_id.id,
        #         'is_invoice_cron': True
        #     }
        #     check_scholarship = self.env['account.move'].create(vals)
        #     price_schedule = self.env['price.schedule'].search([
        #                                                     ('academic_year_id', '=', rec.academic_year_id.id),
        #                                                     ('faculty_id', '=', rec.faculty_id.id),
        #                                                     ('department_id', '=', rec.department_id.id),
        #                                                     ('is_recurring', '=', True)])
        #     scholarship_price = 0
        #     for fee_schedule in price_schedule:
        #         scholarship_price += fee_schedule.fee
        #         check_scholarship.update({
        #             'invoice_line_ids': [(0, 0, {
        #                 'product_id' : fee_schedule.description_id.id,
        #                 'price_unit' : fee_schedule.fee
        #                 })],
        #             })
        #     if price_schedule:
        #         if rec.scholarship_product_id:
        #             scholarship_amount = -((scholarship_price * rec.scholarship_product_id.scholarship_per) / 100)
        #             check_scholarship.update({
        #                 'invoice_line_ids': [(0, 0, {
        #                     'product_id' : rec.scholarship_product_id.id,
        #                     'price_unit' : scholarship_amount
        #                     })],
        #                 })

    def _student_portal_cron_action(self):
        student_ids = self.env['student.registration'].search([('is_user', '=', False), ('student_name_id', '!=', False)])
        print("--ds-d-sdsd", student_ids)
        for student_id in student_ids:
            print("--sd", student_id)
            if student_id.student_name_id and student_id.student_id:
                print("------sdsdda", student_id.student_name_id, student_id.student_id)
                user_ids = self.env['res.users'].search([('login', '=', student_id.student_id)])
                if not user_ids:
                    user_id= self.env['res.users'].create({
                        'login': student_id.student_id,
                        'email': student_id.student_id,
                        'password': student_id.student_id,
                        'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                        'partner_id': student_id.student_name_id.id
                    })
                    student_id.write({'is_user': True, 'student_user_id': user_id.id})

    def name_get(self):
        result = []
        for rec in self:
            if rec.student_id:
                name = str(rec.student_id) + '-' + str(rec.student_name_id.name)
                result.append((rec.id, name))
            else:
                name = str(rec.student_name_id.name)
                result.append((rec.id, name))
        return result

