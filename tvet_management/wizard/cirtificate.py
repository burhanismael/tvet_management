from odoo import api, fields, models, _


class ReExamView(models.TransientModel):
    _name = "certificate.report"
    _description = 'certificate.report'

    class_id = fields.Many2one('class.room', string="Batch Name", required=True)
    date = fields.Date(string="Date")
    # senet_mitting_id = fields.Many2one("senate.mitting",string="Senate Meeting")
    is_medical = fields.Boolean('Medicine')
    # semister_id = fields.Many2one('semester.semester', string="Tier Name", required=True)
    student_id = fields.Many2one('student.registration', string="Student Name")
    serial_no = fields.Char(string="Serial Number", required=True)
    is_privious = fields.Boolean(string="Is Previous")
    previous_class_id = fields.Many2one('class.room', string="Previous Class")

    def pdf_report(self):
        record_data = {
            'class_id': self.class_id.id,
            'student_id': self.student_id.id,
            # 'senet_mitting_id': self.senet_mitting_id.id,
            'date': self.date,
            'is_medical': self.is_medical,
            'serial_no': self.serial_no,
            'previous_class_id': self.previous_class_id.id,
        }
        return self.env.ref('tvet_management.action_certificate_report').report_action(self, data=record_data)

    def pdf_preview_report(self):
        record_data = {
            'class_id': self.class_id.id,
            'student_id': self.student_id.id,
            'senet_mitting_id': self.senet_mitting_id.id,
            'date': self.date,
            'is_medical': self.is_medical,
            'serial_no': self.serial_no,
            'previous_class_id': self.previous_class_id.id,
        }
        return self.env.ref('tvet_management.action_certificate_preview_report').report_action(self, data=record_data)

    @api.onchange('class_id')
    def class_based_domain(self):
        student_ids = self.env['student.registration'].search([('classroom_id', '=', self.class_id.id), ('status', '=', 'enrolled')])
        domain = [('id', 'in', student_ids.ids)]
        return {'domain': {'student_id': domain}}