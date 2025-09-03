# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    discount_refund_pin = fields.Integer()

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    discount_refund_pin = fields.Integer(related='pos_config_id.discount_refund_pin', readonly=False)
