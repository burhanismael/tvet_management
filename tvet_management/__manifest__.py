# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'TVET Management',
    'version': '15.1',
    'category': 'TVET Management',
    'sequence': 1,
    'author': "Merit Advisory",
    'summary': 'TVET Management System',
    'description': "TVET Management System",
    'website': '',
    'depends': ['base', 'account', 'contacts', 'hr', 'hr_expense', 'purchase', 'report_xlsx', 'sale_management', 'website'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/student_registration_seqence.xml',
        'data/nationality_demo.xml',
        'data/invoice_cron.xml',
        'wizard/student_state_wizard.xml',
        'wizard/attendance_report_view.xml',
        'wizard/course_assign.xml',
        'wizard/lecturer_course_assignation_report.xml',
        'wizard/exam_result_report.xml',
        'wizard/exam_result_summary_view.xml',
        'wizard/cirtificate.xml',
        'wizard/testimonial_continues_view.xml',
        'wizard/testimonial_graduation_view.xml',
        'wizard/transcript.xml',
        'wizard/gradution_transcript.xml',
        'views/school_subject_view.xml',
        'views/projects.xml',
        'views/special_need.xml',
        'views/idp_name_view.xml',
        'views/res_company_view.xml',
        'views/student_registration_view.xml',
        'views/course_subject_view.xml',
        'views/res_partner_view.xml',
        'views/res_city_view.xml',
        'views/state_view.xml',
        'views/res_config_settings_views.xml',
        'views/academic_year_view.xml',
        'views/school_shift_view.xml',
        'views/class_room_view.xml',
        'views/school_department_view.xml',
        'views/academic_month_view.xml',
        'views/student_admission_view.xml',
        # 'views/account_move_view.xml',
        'views/awading_system.xml',
        'views/transcript_details.xml',
        'views/assign_course_view.xml',
        'views/semester_view.xml',
        'views/exam_type_view.xml',
        'views/exam_result_view.xml',
        'views/exam_result_entry_view.xml',
        'views/approve_course_view.xml',
        'views/hr_employee_view.xml',
        'views/assign_lecturer_view.xml',
        'views/create_lecturer_view.xml',
        'views/approve_lecturer_view.xml',
        'views/class_location_view.xml',
        'views/manage_timetable_view.xml',
        'views/nationality_view.xml',
        'views/attendance_sheet_view.xml',
        'views/assign_semester_view.xml',
        'views/grading_view.xml',
        'views/portal_chages.xml',
        'views/menu_view.xml',
        'views/student_portal_view.xml',
        'report/attendance_report.xml',
        'report/attandance_report_pdf.xml',
        'report/student_id.xml',
        'report/admission_template.xml',
        'report/transcript_pdf_report.xml',
        'report/exam_report_report.xml',
        'report/exam_result_entry_report.xml',
        'report/exam_summary_report_pdf.xml',
        'report/certificate_pdf.xml',
        'report/testimonial_continues_report.xml',
        'report/testimonial_graduation_report.xml',
        'report/gradution_transcript_pdf_report.xml',
        'report/lecturer_assign_report_pdf.xml',
        'report/student_registration_report.xml',
        'report/course_assing_pdf_report.xml',
        'views/res_users_view.xml',
        'views/hide_portal.xml',
    ],
    'demo': [
    ],
    "assets": {
        'web.assets_frontend': [
            "/tvet_management/static/src/js/student_dashboard.js",
            "/tvet_management/static/src/js/user_error.js"
        ],
        "web.report_assets_common": [
            "/tvet_management/static/src/scss/fonts.css",
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
