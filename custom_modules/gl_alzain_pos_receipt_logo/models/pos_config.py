# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    receipt_logo = fields.Binary()

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    receipt_logo = fields.Binary(related='pos_config_id.receipt_logo', readonly=False)
