# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    def action_validate(self):
        res = super(StockScrap, self).action_validate()
        for scrap in self:
            product = scrap.product_id
            if product.categ_id.inventory_valuation_method != 'automated':
                continue

            category = product.categ_id
            journal = category.valuation_journal_id
            debit_account = category.inventory_scrap_debit_id
            credit_account = category.inventory_scrap_credit_id

            if not (debit_account and credit_account and journal):
                raise UserError("Missing configuration on product category for scrap accounting.")
            if category.property_cost_method == 'fifo':
                valuation_amount = 0.0
                valuation_layers = self.env['stock.valuation.layer'].search([
                    ('product_id', '=', product.id),
                    ('remaining_qty', '>', 0),
                ], order='create_date ASC')

                qty_to_value = scrap.scrap_qty
                for layer in valuation_layers:
                    qty_used = min(layer.remaining_qty, qty_to_value)
                    valuation_amount += qty_used * (layer.unit_cost or 0.0)
                    qty_to_value -= qty_used
                    if qty_to_value <= 0:
                        break

            if category.property_cost_method == 'standard':
                valuation_amount = product.standard_price * scrap.scrap_qty

            move_vals = {
                'journal_id': journal.id,
                'date': fields.Date.context_today(scrap),
                'ref': f'Scrap: {scrap.name or scrap.id}',
                'move_type': 'entry',
                'line_ids': [
                    (0, 0, {
                        'account_id': debit_account.id,
                        'name': f'Scrap of {product.display_name}',
                        'debit': valuation_amount,
                        'credit': 0.0,
                        'product_id': product.id,
                        'quantity': scrap.scrap_qty,
                    }),
                    (0, 0, {
                        'account_id': credit_account.id,
                        'name': f'Scrap of {product.display_name}',
                        'debit': 0.0,
                        'credit': valuation_amount,
                        'product_id': product.id,
                        'quantity': scrap.scrap_qty,
                    }),
                ],
            }

            self.env['account.move'].create(move_vals).action_post()

        return res
