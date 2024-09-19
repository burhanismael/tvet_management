# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.payment import utils as payment_utils
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager


class StudentPortal(portal.CustomerPortal):

    @http.route(['/my/timetable'], type='http', auth="user", website=True)
    def portal_my_timetable(self, **kw):
        values = self._prepare_portal_layout_values()
        # partner = request.env.user.partner_id
        timetable = request.env['manage.timetable']
        sale_details = timetable.sudo().search([])
        return request.render('tvet_management.portal_my_timetable', {'my_details': sale_details})

