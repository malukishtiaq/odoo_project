# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductCategory(models.Model):
    _inherit = 'product.category'

    inventory_valuation_method = fields.Selection([
        ('manual', 'Manual'),
        ('automated', 'Automated'),
    ], string='Valuation Type')
    valuation_journal_id = fields.Many2one('account.journal', string='Associated Journal')
    inventory_valuation_account_id = fields.Many2one('account.account', string='Inventory Valuation')
    stock_output_account_id = fields.Many2one('account.account', string='Stock Output Account')
    stock_input_account_id = fields.Many2one('account.account', string='Stock Input Account')
    inventory_adjustment_credit_id = fields.Many2one('account.account', string='Inventory Adjustment Credit Account')
    inventory_adjustment_debit_id = fields.Many2one('account.account', string='Inventory Adjustment Debit Account')
    inventory_scrap_credit_id = fields.Many2one('account.account', string='Inventory Scrap Credit Account')
    inventory_scrap_debit_id = fields.Many2one('account.account', string='Inventory Scrap Debit Account')
    property_cost_method = fields.Selection([
        ('standard', 'Standard Price'),
        ('fifo', 'First In First Out (FIFO)'),
        ('average', 'Average Cost (AVCO)')], string="Costing Method",
        company_dependent=True, copy=True,
        help="""Standard Price: The products are valued at their standard cost defined on the product.
            Average Cost (AVCO): The products are valued at weighted average cost.
            First In First Out (FIFO): The products are valued supposing those that enter the company first will also leave it first.
            """,
        tracking=True, default='fifo'
    )

