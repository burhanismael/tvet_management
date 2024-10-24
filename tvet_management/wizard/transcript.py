from odoo import api, fields, models, _


class ReExamView(models.TransientModel):
    _name = "result.transcript.report"
    _description = 'result.slip.report'

    class_ids = fields.Many2one('class.room', string="Batch Name", required=True)
    semister_id = fields.Selection([('six', '6 Semester'), ('eight', '8 Semester')], string="Tier Type")
    student_id = fields.Many2one('student.registration', string="Student Name")
    date = fields.Date(string='Date')
    is_privious = fields.Boolean(string="Is Previous")
    previous_class_id = fields.Many2one('class.room', string="Previous Class")

    def pdf_report(self):
        record_data = {
            'class_id': self.class_ids.id,
            'semister_id': self.semister_id,
            'student_id': self.student_id.id,
            'issu_date': self.date,
            'previous_class_id': self.previous_class_id.id,
        }
        return self.env.ref('tvet_management.action_trascript_report').report_action(self, data=record_data)

    def pdf_preview_report(self):
        record_data = {
            'class_id': self.class_ids.id,
            'semister_id': self.semister_id,
            'student_id': self.student_id.id,
            'issu_date': self.date,
            'previous_class_id': self.previous_class_id.id,
        }
        return self.env.ref('tvet_management.action_trascript_preview_report').report_action(self, data=record_data)

    @api.onchange('class_ids')
    def class_based_domain(self):
        student_ids = self.env['student.registration'].search([('classroom_id', '=', self.class_ids.id), ('status', '=', 'enrolled')])
        domain = [('id', 'in', student_ids.ids)]
        return {'domain': {'student_id': domain}}
