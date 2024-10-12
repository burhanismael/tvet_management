from odoo import api, fields, models, _


class AttendanceView(models.TransientModel):
    _name = "exam.result.report"

    class_id = fields.Many2one('class.room', string="Class Name", required=True)
    acadamic_year_id = fields.Many2one('academic.year', string="Academic Year", required=True)
    semister_id = fields.Many2one('semester.semester', string="Semester Name", required=True, domain="[('class_id', '=', class_id)]")
    student_id = fields.Many2one('student.registration', string="Student Name")
    is_privious = fields.Boolean(string="Is Transfer")
    previous_class_id = fields.Many2one('class.room', string="Previous Class")

    def get_grading_policy(self, total_mark):
        grade_policy_id = self.env['grading.policy'].search([('minimum', '<=', total_mark), ('maximum', '>=', total_mark), ('is_medical', '=', False)], limit=1)
        return grade_policy_id.grade

    def excle_download_action_exam_result(self):
        data = {
               'class_id':self.class_id.id,
               'acadamic_year_id':self.acadamic_year_id.id,
               'semister_id': self.semister_id.id,
               'student_id': self.student_id.id if self.student_id else False,
               'previous_class_id': self.previous_class_id.id,
        }
        return self.env.ref('tvet_management.exam_report_xlsx').report_action(self, data=data)

    @api.onchange('class_id')
    def class__student_based_domain(self):
        student_ids = self.env['student.registration'].search([('classroom_id', '=', self.class_id.id), ('status', '=', 'enrolled')])
        domain = [('id', 'in', student_ids.ids)]
        return {'domain': {'student_id': domain}}

    @api.onchange('class_id')
    def class_based_domain(self):
        if self.class_id:
            semister_ids = self.class_id.class_room_ids.mapped('semester_id')
            domain = [('id', 'in', semister_ids.ids)]
            return {'domain': {'semister_id': domain}}

    def pdf_preview_report(self):
        data = {
               'class_id':self.class_id.id,
               'acadamic_year_id':self.acadamic_year_id.id,
               'semister_id': self.semister_id.id,
               'student_id': self.student_id.id if self.student_id else False,
               'previous_class_id': self.previous_class_id.id,
        }
        return self.env.ref('tvet_management.exam_report_report').report_action(self, data=data)

    # @api.onchange('class_id')
    # def class_based_domain(self):
    #     room_ids = self.env['class.room'].search([('name', '=', self.class_id.name)])
    #     semister_ids = room_ids.mapped('semester_id')
    #     domain = [('id', 'in', semister_ids.ids)]
    #     return {'domain': {'semister_id': domain}}
