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
    'depends': ['base', 'account', 'contacts', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/student_registration_seqence.xml',
        'views/academic_year_view.xml',
        'views/projects.xml',
        'views/school_department_view.xml',
        'views/school_course_view.xml',
        'views/school_subject_view.xml',
        'views/school_city_view.xml',
        'views/school_class_room_view.xml',
        'views/school_semester_view.xml',
        'views/school_shift_view.xml',
        'views/student_registration_view.xml',


        'views/menu_items.xml',
        
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
