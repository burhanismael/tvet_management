from odoo import api, fields, models, _


class GradutionView(models.TransientModel):
    _name = "gradution.transcript.report"
    _description = 'gradution.slip.report'

    class_id = fields.Many2one('class.room', string="Class Name", required=True)
    semister_id = fields.Selection([('six', '6 Semester'), ('eight', '8 Semester')], string="Semester Type")
    student_id = fields.Many2one('student.registration', string="Student Name")
    date = fields.Date(string='Date')
    is_privious = fields.Boolean(string="Is Previous")
    previous_class_id = fields.Many2one('class.room', string="Previous Class")

    def pdf_report(self):
        record_data = {
            'class_id': self.class_id.id,
            'semister_id': self.semister_id,
            'student_id': self.student_id.id,
            'issu_date': self.date,
            'previous_class_id': self.previous_class_id.id
        }
        return self.env.ref('tvet_management.action_gradution_trascript_report').report_action(self, data=record_data)

    def pdf_preview_report(self):
        record_data = {
            'class_id': self.class_id.id,
            'semister_id': self.semister_id,
            'student_id': self.student_id.id,
            'issu_date': self.date,
            'previous_class_id': self.previous_class_id.id
        }
        return self.env.ref('tvet_management.action_gradution_trascript_preview_report').report_action(self, data=record_data)

    @api.onchange('class_id')
    def class_based_domain(self):
        student_ids = self.env['student.registration'].search([('classroom_id', '=', self.class_id.id), ('status', '=', 'enrolled')])
        domain = [('id', 'in', student_ids.ids)]
        return {'domain': {'student_id': domain}}
