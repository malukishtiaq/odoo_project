# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from collections import defaultdict


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _action_done(self):
        res = super(StockPicking, self)._action_done()
        for picking in self:
            if picking.picking_type_id.code in ['incoming', 'outgoing']:
                self.create_inventory_valuation_entries()
        return res

    def create_inventory_valuation_entries(self):
        for picking in self:
            AccountMove = self.env['account.move']
            grouped_moves = defaultdict(list)

            # Group stock moves by category
            for move in picking.move_ids_without_package.filtered(lambda m: m.product_id.categ_id.inventory_valuation_method == 'automated'):
                category = move.product_id.categ_id
                grouped_moves[category].append(move)

            for category, moves in grouped_moves.items():
                journal = category.valuation_journal_id
                stock_valuation_account = category.inventory_valuation_account_id.id
                stock_input_account = category.stock_input_account_id.id
                stock_output_account = category.stock_output_account_id.id
                # cogs_account = category.property_account_expense_categ_id.id

                line_vals = []

                for move in moves:
                    product = move.product_id
                    if product.cost_method == 'fifo':
                        valuation_layer = move.stock_valuation_layer_ids.sorted('create_date')
                        if valuation_layer:
                            valuation_amount = move.stock_valuation_layer_ids.sorted('create_date')[-1].value
                    else:
                        valuation_amount = product.standard_price * move.product_uom_qty

                    if picking.picking_type_id.code == 'incoming':
                        debit_account = stock_valuation_account
                        credit_account = stock_input_account
                    elif picking.picking_type_id.code == 'outgoing':
                        debit_account = stock_output_account
                        credit_account = stock_valuation_account
                    else:
                        continue

                    line_vals.append((0, 0, {
                        'account_id': debit_account,
                        'debit': abs(valuation_amount),
                        'credit': 0.0,
                        'name': move.name,
                        'product_id': product.id,
                        'quantity': move.product_uom_qty,
                    }))
                    line_vals.append((0, 0, {
                        'account_id': credit_account,
                        'credit': abs(valuation_amount),
                        'debit': 0.0,
                        'name': move.name,
                        'product_id': product.id,
                        'quantity': move.product_uom_qty,
                    }))

                if line_vals:
                    AccountMove.create({
                        'journal_id': journal.id,
                        'date': picking.scheduled_date or fields.Date.context_today(picking),
                        'ref': picking.name,
                        'line_ids': line_vals,
                    }).action_post()

