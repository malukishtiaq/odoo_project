# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PriceConfigurator(models.Model):
    _name = 'module.price.configurator'
    _description = 'Module Price Configurator'
    _rec_name = 'module_id'

    module_id = fields.Many2one('ir.module.module', string='Module')
    price_unit = fields.Monetary(string='Price')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

