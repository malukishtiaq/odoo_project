# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class POSPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    default_partner_id = fields.Many2one("res.partner", "Default Customer")

    @api.model
    def _load_pos_data_fields(self, config_id):
        return super(POSPaymentMethod, self)._load_pos_data_fields(config_id) + ['default_partner_id']
