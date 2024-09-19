from odoo import models, fields, api


class HideMenuUser(models.Model):
    _inherit = 'res.users'


    def write(self, vals):
        # if vals.get('is_student'):
        #     view_attendance_menu = self.env.ref('tvet_management.menu_open_att_view_view_view')
        #     view_timetable_menu = self.env.ref('tvet_management.manage_timetable_menu_read')
        #     view_academic_menu = self.env.ref('tvet_management.menu_student_academic')
        #     view_university_main_menu = self.env.ref('tvet_management.menu_tvet_management_main')
        #     all_menu_ids = self.env['ir.ui.menu'].search([('id', 'not in', [view_timetable_menu.id,
        #                                                                     view_academic_menu.id,
        #                                                                     view_university_main_menu.id,
        #                                                                     view_attendance_menu.id,
        #                                                                     ])])
        #     vals.update({'hide_menu_ids': [(6, 0, all_menu_ids.ids)]})
        if vals.get('is_lecturer'):
            menu_open_att_view_view = self.env.ref('tvet_management.menu_open_att_view_view')
            view_attendance_menu = self.env.ref('tvet_management.menu_open_att_view_view_view')
            view_timetable_menu = self.env.ref('tvet_management.manage_timetable_menu_read')
            view_academic_menu = self.env.ref('tvet_management.menu_student_academic')
            view_university_main_menu = self.env.ref('tvet_management.menu_tvet_management_main')
            all_menu_ids = self.env['ir.ui.menu'].search([('id', 'not in', [view_timetable_menu.id,
                                                                            view_academic_menu.id,
                                                                            view_university_main_menu.id,
                                                                            view_attendance_menu.id,
                                                                            menu_open_att_view_view.id,
                                                                            ])])
            vals.update({'hide_menu_ids': [(6, 0, all_menu_ids.ids)]})

        # if vals.get('is_student') in [False, None] and vals.get('is_lecturer') in [False, None]:
        #     vals.update({'hide_menu_ids': [(6, 0, [])]})
        res = super(HideMenuUser, self).write(vals)
        # group_one = self.env.ref('tvet_management.hr_manager_officer_access')
        # group_two = self.env.ref('tvet_management.hr_officer_group_access')
        # if group_one.id in self.groups_id.ids and group_two.id in self.groups_id.ids:
        #     group_two.write({'users': [(3, self.id)]})
        # elif group_one.id not in self.groups_id.ids:
        #     group_two.write({'users': [(4, self.id)]})
        self.clear_caches()
        return res
