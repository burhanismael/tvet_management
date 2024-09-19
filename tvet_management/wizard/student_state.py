from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StudentState(models.TransientModel):
    _name = 'student.state.wizard'
    _description = "This is without which will update information of student."

    status = fields.Selection([('enrolled','Enrolled'),('drop_out','Drop Out'),('inactive','Inactive'),('graduated','Graduated')])
    reason = fields.Char(string='Reason')

    def update_info(self):
        student_ids = self.env.context.get('active_ids', [])
        student = self.env['student.registration'].browse(student_ids)
        if not self.status:
                raise ValidationError('Please select anyone')
        else:
            student.status = self.status
