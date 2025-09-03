# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_created_from_pos = fields.Boolean("Created from POS?")

    @api.onchange('name')
    def onchange_name(self):
        if self.name and not self.phone:
            try:
                self.phone = int(self.name)
            except:
                pass

    @api.model
    def _load_pos_data_domain(self, data):
        config_id = self.env['pos.config'].browse(data['pos.config']['data'][0]['id'])
        # Collect partner IDs from loaded orders
        loaded_order_partner_ids = {order['partner_id'] for order in data['pos.order']['data']}

        # Extract partner IDs from the tuples returned by get_limited_partners_loading
        limited_partner_ids = {partner[0] for partner in config_id.get_limited_partners_loading()}

        limited_partner_ids.add(self.env.user.partner_id.id)  # Ensure current user is included
        partner_ids = limited_partner_ids.union(loaded_order_partner_ids)

        # Collect partner IDs from loaded POS Payment method
        loaded_payment_method_partner_ids = {method['default_partner_id'] for method in
                                             data['pos.payment.method']['data']}
        partner_ids = partner_ids.union(loaded_payment_method_partner_ids)
        return [('id', 'in', list(partner_ids))]

    @api.model
    def _load_pos_data_fields(self, config_id):
        return super()._load_pos_data_fields(config_id) + ['is_created_from_pos']
