from odoo import api, fields, models, _


class AttendanceView(models.TransientModel):
    _name = "exam.summary.report"

    class_id = fields.Many2one('class.room', string="Class Name", required=True)
    acadamic_year_id = fields.Many2one('academic.year', string="Academic Year", required=True)
    semister_id = fields.Many2one('semester.semester', string="Semester Name", required=True, domain="[('class_id', '=', class_id)]")
    student_id = fields.Many2one('student.registration', string="Student Name")
    is_privious = fields.Boolean(string="Is Previous")
    previous_class_id = fields.Many2one('class.room', string="Previous Class")


    def excle_download_action_summary_result(self):
        data = {
               'class_id':self.class_id.id,
               'acadamic_year_id':self.acadamic_year_id.id,
               'semister_id': self.semister_id.id,
               'student_id': self.student_id.id if self.student_id else False,
               'previous_class_id': self.previous_class_id.id,
        }
        return self.env.ref('tvet_management.exam_summary_report_xlsx').report_action(self, data=data)

    @api.onchange('class_id')
    def class_based_domain(self):
        student_ids = self.env['student.registration'].search([('classroom_id', '=', self.class_id.id), ('status', '=', 'enrolled')])
        domain = [('id', 'in', student_ids.ids)]
        return {'domain': {'student_id': domain}}

    def get_reexam_data(self, student_id, cource_exam_ids, course_ids, semister_id):
        reexamcource = []
        reexamdetails = ''
        for cource in course_ids:
            line_ids = cource_exam_ids.filtered(lambda x:x.course_name_id.id == cource.id and x.semester_id.sem_number == semister_id.sem_number).mapped('student_ids').filtered(lambda x:x.student_id.id == student_id.id)
            total_mark = sum(line_ids.mapped('marks'))
            grade_policy_id = self.env['grading.policy'].search([('minimum', '<=', total_mark),('maximum', '>=', total_mark)], limit=1)
            if grade_policy_id.grade == 'F':
                reexamcource.append(cource.course_name)
        if reexamcource:
            reexamdetails = ",".join(reexamcource)
        return reexamdetails

    @api.onchange('class_id')
    def class_based_semister_domain(self):
        if self.class_id:
            semister_ids = self.class_id.class_room_ids.mapped('semester_id')
            domain = [('id', 'in', semister_ids.ids)]
            return {'domain': {'semister_id': domain}}

    def pdf_download_action(self):
        data = {
               'class_id':self.class_id.id,
               'acadamic_year_id':self.acadamic_year_id.id,
               'semister_id': self.semister_id.id,
               'student_id': self.student_id.id if self.student_id else False,
               'previous_class_id': self.previous_class_id.id,
        }
        return self.env.ref('tvet_management.exam_summary_report_pdf').report_action(self, data=data)

    # @api.onchange('class_id')
    # def class_based_domain(self):
    #     room_ids = self.env['class.room'].search([('name', '=', self.class_id.name)])
    #     semister_ids = room_ids.mapped('semester_id')
    #     domain = [('id', 'in', semister_ids.ids)]
    #     return {'domain': {'semister_id': domain}}
