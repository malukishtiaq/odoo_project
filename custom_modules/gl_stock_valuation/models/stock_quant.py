# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _get_fifo_value(self, quantity):
        self.ensure_one()
        product = self.product_id

        if not product or product.categ_id.property_cost_method != 'fifo':
            return product.standard_price * quantity

        layers = self.env['stock.valuation.layer'].search([
            ('product_id', '=', product.id),
            ('remaining_qty', '>', 0),
        ], order='create_date ASC')

        total_value = 0.0
        qty_to_value = quantity

        for layer in layers:
            layer_qty = layer.remaining_qty
            taken_qty = min(qty_to_value, layer_qty)
            total_value += taken_qty * (layer.remaining_value / layer.remaining_qty)
            qty_to_value -= taken_qty
            if qty_to_value <= 0:
                break

        if qty_to_value > 0:
            # Not enough FIFO layers, fallback
            total_value += qty_to_value * product.standard_price

        return total_value

    def action_apply_inventory(self):
        for adj in self:
            AccountMove = self.env['account.move']
            # AccountMoveLine = self.env['account.move.line']

            # grouped_data = {}
            for quant in self:
                product = quant.product_id
                if product.categ_id.inventory_valuation_method != 'automated':
                    continue

                categ = product.categ_id
                inventory_account = categ.inventory_adjustment_credit_id.id
                valuation_account = categ.inventory_adjustment_debit_id.id
                journal = categ.valuation_journal_id.id

                if not (inventory_account and valuation_account and journal):
                    raise UserError(f"Missing account/journal setup in category: {categ.name}")

                qty_diff = quant.inventory_quantity - quant.quantity
                if qty_diff == 0:
                    continue
                if product.categ_id.property_cost_method == 'fifo':
                    cost = quant._get_fifo_value(quantity=abs(qty_diff))
                elif product.property_cost_method == 'average':
                    cost = product.standard_price * abs(qty_diff)
                else:
                    cost = product.standard_price * abs(qty_diff)

                line_vals = []

                if qty_diff > 0:  # Gain
                    line_vals.append((0, 0, {
                        'account_id': valuation_account,
                        'name': f"Inventory Gain: {product.display_name}",
                        'debit': cost,
                        'credit': 0.0,
                        'product_id': product.id,
                        'quantity': abs(qty_diff),
                    }))
                    line_vals.append((0, 0, {
                        'account_id': inventory_account,
                        'name': f"Inventory Gain: {product.display_name}",
                        'credit': cost,
                        'debit': 0.0,
                        'product_id': product.id,
                        'quantity': abs(qty_diff),
                    }))
                else:  # Loss
                    line_vals.append((0, 0, {
                        'account_id': inventory_account,
                        'name': f"Inventory Loss: {product.display_name}",
                        'debit': cost,
                        'credit': 0.0,
                        'product_id': product.id,
                        'quantity': abs(qty_diff),
                    }))
                    line_vals.append((0, 0, {
                        'account_id': valuation_account,
                        'name': f"Inventory Loss: {product.display_name}",
                        'credit': cost,
                        'debit': 0.0,
                        'product_id': product.id,
                        'quantity': abs(qty_diff),
                    }))

                move = AccountMove.create({
                    'journal_id': journal,
                    'ref': f"Inventory Adjustment - {product.name}",
                    'move_type': 'entry',
                    'line_ids': line_vals,
                    'date': fields.Date.today(),
                })
                move.action_post()
        return super(StockQuant, self).action_apply_inventory()
