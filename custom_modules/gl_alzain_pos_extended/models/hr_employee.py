# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class Employee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['name', 'user_id', 'work_contact_id']

    @api.model
    def _load_pos_data_domain(self, data):
        return []

class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def _load_pos_data_models(self, config_id):
        data = super()._load_pos_data_models(config_id)
        data += ['hr.employee']
        return data
