# -*- coding: utf-8 -*-

from odoo import fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    order_employee_id = fields.Many2one('hr.employee', string='Order Employee')
