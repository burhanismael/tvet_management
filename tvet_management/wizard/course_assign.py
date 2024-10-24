from odoo import api, fields, models, _


class ReexamUpdates(models.TransientModel):
    _name = "course.assign.export"
    _description = 'course.assign.export'

    department_id = fields.Many2one('school.department', string="Department", required=True)
    class_id = fields.Many2one('class.room', string="Batch Name")
    semister_id = fields.Many2one('semester.semester', string="Tier Name", domain="[('class_id', '=', class_id)]")
    aca_id = fields.Many2one('academic.year', string="Academic Year")

    @api.onchange('department_id')
    def department_based_domain(self):
        if self.department_id:
            class_ids = self.env['class.room'].search([('school_department_id.id', '=', self.department_id.id)])
            domain = [('id', 'in', class_ids.ids)]
            return {'domain': {'class_id': domain}}

    @api.onchange('class_id')
    def class_based_domain(self):
        if self.class_id:
            semister_ids = self.class_id.class_room_ids.mapped('semester_id')
            domain = [('id', 'in', semister_ids.ids)]
            return {'domain': {'semister_id': domain}}


    def export_report(self):
        data = {
            'department_id': self.department_id.name,
            'class_id': self.class_id.name,
            'semister_id': self.semister_id.semester_name,

        }
        return self.env.ref('tvet_management.course_assign_export_xlsx').report_action(self, data=data)

    def export_pdf_report(self):
            data = {
                'aca_id': self.aca_id.id,
                'department_id': self.department_id.name,
                'class_id': self.class_id.name,
                'semister_id': self.semister_id.semester_name,

            }
            return self.env.ref('tvet_management.action_course_assign_report').report_action(self, data=data)

    def export_pdf_preview_report(self):
            data = {
                'aca_id': self.aca_id.id,
                'department_id': self.department_id.name,
                'class_id': self.class_id.name,
                'semister_id': self.semister_id.semester_name,

            }
            return self.env.ref('tvet_management.action_course_assign_preview_report').report_action(self, data=data)
