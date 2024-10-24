from odoo import api, fields, models, _


class LecturerCourseAssign(models.TransientModel):
    _name = "lecturer.assign.report"
    _description = 'lecturer.assign.report'

    aca_id = fields.Many2one('academic.year', string="Academic Year")
    lecturer_id = fields.Many2one('create.lecturer', "Lecturer name", required=True)
    dep_id = fields.Many2one('school.department', string="Department")
    class_id = fields.Many2one('class.room', string="Batch Name")
    sem_id = fields.Many2many('semester.semester', string="Tier")

    @api.onchange('dep_id')
    def department_based_domain(self):
        if self.dep_id:
            class_ids = self.env['class.room'].search([('school_department_id.id', '=', self.dep_id.id)])
            domain = [('id', 'in', class_ids.ids)]
            return {'domain': {'class_id': domain}}

    @api.onchange('class_id')
    def class_based_domain(self):
        if self.class_id:
            semister_ids = self.class_id.class_room_ids.mapped('semester_id')
            domain = [('id', 'in', semister_ids.ids)]
            return {'domain': {'sem_id': domain}}


    def print_pdf_report(self):
        data = {
            'aca_id': self.aca_id.id,
            'lecturer_id': self.lecturer_id.name,
            'dep_id': self.dep_id.name,
            'class_id': self.class_id.name,
            'sem_id': self.sem_id.ids,

        }
        return self.env.ref('tvet_management.action_lecturer_course_report').report_action(self, data=data)