# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import uuid
import logging

_logger = logging.getLogger(__name__)


class PricingPriceList(models.Model):
    """Price list for pricing scenarios"""
    _name = 'pricing.price.list'
    _description = 'Pricing Scenario Price List'
    _order = 'create_date desc'

    name = fields.Char('Name', required=True)
    month_key = fields.Char('Month', required=True, help='Month in YYYY-MM format')
    branch_id = fields.Many2one('res.partner', string='Branch', help='Optional branch filter')
    source_scenario = fields.Selection([
        ('break_even', 'Break Even'),
        ('net_10k', '+10,000 AED Net'),
        ('net_custom', '+Custom Net')
    ], string='Source Scenario', required=True)
    mode = fields.Selection([
        ('uniform', 'Uniform'),
        ('weighted', 'Weighted')
    ], string='Uplift Mode', required=True)
    target = fields.Float('Target Amount', help='Target net profit amount')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived')
    ], string='Status', default='draft', required=True)
    
    # Audit fields
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    created_at = fields.Datetime('Created At', default=fields.Datetime.now)
    activated_by = fields.Many2one('res.users', string='Activated By')
    activated_at = fields.Datetime('Activated At')
    
    # Summary fields
    products_count = fields.Integer('Products Count', compute='_compute_summary')
    min_pct = fields.Float('Min % Change', compute='_compute_summary')
    max_pct = fields.Float('Max % Change', compute='_compute_summary')
    floors_triggered = fields.Integer('Floors Triggered', compute='_compute_summary')
    
    # Lines
    line_ids = fields.One2many('pricing.price.list.item', 'price_list_id', string='Price Items')
    
    @api.depends('line_ids')
    def _compute_summary(self):
        """Compute summary statistics"""
        for record in self:
            if record.line_ids:
                record.products_count = len(record.line_ids)
                record.min_pct = min(line.pct_change for line in record.line_ids)
                record.max_pct = max(line.pct_change for line in record.line_ids)
                record.floors_triggered = len(record.line_ids.filtered('floor_applied'))
            else:
                record.products_count = 0
                record.min_pct = 0.0
                record.max_pct = 0.0
                record.floors_triggered = 0

    def action_activate(self):
        """Activate the price list"""
        if not self.env.user.has_group('dashboard_pos.group_pricing_admin'):
            raise UserError('Only Pricing Administrators can activate price lists.')
        
        if self.status != 'draft':
            raise UserError('Only draft price lists can be activated.')
        
        # Archive any existing active price lists for the same month/branch
        existing_active = self.search([
            ('month_key', '=', self.month_key),
            ('branch_id', '=', self.branch_id.id if self.branch_id else False),
            ('status', '=', 'active')
        ])
        existing_active.write({'status': 'archived'})
        
        # Activate this price list
        self.write({
            'status': 'active',
            'activated_by': self.env.user.id,
            'activated_at': fields.Datetime.now()
        })
        
        # Apply the prices to products
        self._apply_prices_to_products()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Price List Activated',
                'message': f'Price list "{self.name}" has been activated successfully.',
                'type': 'success'
            }
        }

    def _apply_prices_to_products(self):
        """Apply the new prices to products"""
        for line in self.line_ids:
            try:
                # Find the product template
                product_template = self.env['product.template'].search([
                    ('name', '=', line.product_name),
                    ('available_in_pos', '=', True)
                ], limit=1)
                
                if product_template:
                    # Update the list price
                    product_template.write({'list_price': line.new_price})
                    _logger.info(f"Updated price for {line.product_name}: {line.old_price} -> {line.new_price}")
                else:
                    _logger.warning(f"Product not found: {line.product_name}")
                    
            except Exception as e:
                _logger.error(f"Error updating price for {line.product_name}: {e}")


class PricingPriceListItem(models.Model):
    """Price list items for pricing scenarios"""
    _name = 'pricing.price.list.item'
    _description = 'Pricing Scenario Price List Item'

    price_list_id = fields.Many2one('pricing.price.list', string='Price List', required=True, ondelete='cascade')
    product_name = fields.Char('Product Name', required=True)
    old_price = fields.Float('Old Price', required=True)
    new_price = fields.Float('New Price', required=True)
    pct_change = fields.Float('Percentage Change', required=True)
    floor_applied = fields.Boolean('Cost Floor Applied', default=False)
    
    @api.constrains('new_price')
    def _check_new_price(self):
        """Ensure new price is not negative"""
        for record in self:
            if record.new_price < 0:
                raise ValidationError('New price cannot be negative.')
