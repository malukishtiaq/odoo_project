# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    refund_line_is_component = fields.Boolean('Component?', related='refunded_orderline_id.is_component', readonly=True, store=True, index=True)
    is_component = fields.Boolean('Component?')

    def get_component_status(self):
        try:
            component = self.is_component
            return component
        except Exception as e:
            return False
