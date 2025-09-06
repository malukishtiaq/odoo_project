# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class TestActionButtons(TransactionCase):
    """Test action buttons functionality"""

    def setUp(self):
        super().setUp()
        self.pos_order_model = self.env['pos.order']
        self.price_list_model = self.env['pricing.price.list']
        self.price_list_item_model = self.env['pricing.price.list.item']
        self.product_template_model = self.env['product.template']
        
        # Create test company
        self.company = self.env.company
        
        # Create test products
        self.product_a = self.product_template_model.create({
            'name': 'Product A',
            'available_in_pos': True,
            'list_price': 100.0,
            'standard_price': 80.0,
            'company_id': self.company.id
        })
        
        self.product_b = self.product_template_model.create({
            'name': 'Product B',
            'available_in_pos': True,
            'list_price': 80.0,
            'standard_price': 60.0,
            'company_id': self.company.id
        })

    def test_apply_pricing_scenarios_dry_run(self):
        """Test applying pricing scenarios in dry run mode"""
        # Mock the get_pricing_scenarios method to return test data
        def mock_get_pricing_scenarios(month):
            return {
                'status': 'ok',
                'month': month,
                'totals': {'R': 10000, 'G': 1950, 'E': 1800, 'N': 150, 'x_min': 0},
                'scenarios': {
                    'break_even': [
                        {
                            'product': 'Product A',
                            'qty': 50.0,
                            'cost': 80.0,
                            'price_real': 100.0,
                            'price_target': 98.0,
                            'diff': 2.0,
                            'diff_pct': 2.04
                        }
                    ],
                    'net_10k': {
                        'uniform': {
                            'x': 0.985,
                            'rows': [
                                {
                                    'product': 'Product A',
                                    'qty': 50.0,
                                    'cost': 80.0,
                                    'price_real': 100.0,
                                    'price_target': 198.5,
                                    'pct': 98.5,
                                    'margin_after': 59.7
                                }
                            ]
                        },
                        'weighted': {
                            'x_budget': 0.985,
                            'x_range': [98.5, 98.5],
                            'rows': [
                                {
                                    'product': 'Product A',
                                    'qty': 50.0,
                                    'cost': 80.0,
                                    'price_real': 100.0,
                                    'price_target': 198.5,
                                    'pct': 98.5,
                                    'margin_after': 59.7
                                }
                            ]
                        }
                    }
                }
            }
        
        # Patch the method
        original_method = self.pos_order_model.get_pricing_scenarios
        self.pos_order_model.get_pricing_scenarios = mock_get_pricing_scenarios
        
        try:
            # Test dry run for break-even scenario
            result = self.pos_order_model.apply_pricing_scenarios(
                month='2024-01',
                scenario='break_even',
                mode='uniform',
                dry_run=True
            )
            
            self.assertEqual(result['status'], 'preview')
            self.assertEqual(result['summary']['products'], 1)
            self.assertEqual(result['summary']['min_pct'], 0.0204)
            self.assertEqual(result['summary']['max_pct'], 0.0204)
            self.assertEqual(result['summary']['floors_triggered'], 0)
            
        finally:
            # Restore original method
            self.pos_order_model.get_pricing_scenarios = original_method

    def test_apply_pricing_scenarios_create_price_list(self):
        """Test creating actual price list"""
        # Mock the get_pricing_scenarios method
        def mock_get_pricing_scenarios(month):
            return {
                'status': 'ok',
                'month': month,
                'totals': {'R': 10000, 'G': 1950, 'E': 1800, 'N': 150, 'x_min': 0},
                'scenarios': {
                    'net_10k': {
                        'uniform': {
                            'x': 0.985,
                            'rows': [
                                {
                                    'product': 'Product A',
                                    'qty': 50.0,
                                    'cost': 80.0,
                                    'price_real': 100.0,
                                    'price_target': 198.5,
                                    'pct': 98.5,
                                    'margin_after': 59.7
                                }
                            ]
                        }
                    }
                }
            }
        
        # Patch the method
        original_method = self.pos_order_model.get_pricing_scenarios
        self.pos_order_model.get_pricing_scenarios = mock_get_pricing_scenarios
        
        try:
            # Test creating price list
            result = self.pos_order_model.apply_pricing_scenarios(
                month='2024-01',
                scenario='net_10k',
                mode='uniform',
                dry_run=False,
                idempotency_key='test-key-123'
            )
            
            self.assertEqual(result['status'], 'draft')
            self.assertIn('price_list_id', result)
            
            # Check that price list was created
            price_list = self.price_list_model.browse(result['price_list_id'])
            self.assertEqual(price_list.name, 'net_10k_uniform_2024-01_10000_test-key-123')
            self.assertEqual(price_list.month_key, '2024-01')
            self.assertEqual(price_list.source_scenario, 'net_10k')
            self.assertEqual(price_list.mode, 'uniform')
            self.assertEqual(price_list.target, 10000)
            self.assertEqual(price_list.status, 'draft')
            
            # Check that price list items were created
            items = price_list.line_ids
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].product_name, 'Product A')
            self.assertEqual(items[0].old_price, 100.0)
            self.assertEqual(items[0].new_price, 198.5)
            self.assertEqual(items[0].pct_change, 0.985)
            self.assertFalse(items[0].floor_applied)
            
        finally:
            # Restore original method
            self.pos_order_model.get_pricing_scenarios = original_method

    def test_apply_pricing_scenarios_idempotency(self):
        """Test idempotency key prevents duplicate price lists"""
        # Create existing price list with same idempotency key
        existing_price_list = self.price_list_model.create({
            'name': 'test_existing_key-123',
            'month_key': '2024-01',
            'source_scenario': 'net_10k',
            'mode': 'uniform',
            'target': 10000,
            'status': 'draft'
        })
        
        # Mock the get_pricing_scenarios method
        def mock_get_pricing_scenarios(month):
            return {
                'status': 'ok',
                'month': month,
                'scenarios': {'net_10k': {'uniform': {'rows': []}}}
            }
        
        # Patch the method
        original_method = self.pos_order_model.get_pricing_scenarios
        self.pos_order_model.get_pricing_scenarios = mock_get_pricing_scenarios
        
        try:
            # Test with same idempotency key
            result = self.pos_order_model.apply_pricing_scenarios(
                month='2024-01',
                scenario='net_10k',
                mode='uniform',
                dry_run=False,
                idempotency_key='test_existing_key-123'
            )
            
            self.assertEqual(result['status'], 'draft')
            self.assertEqual(result['price_list_id'], existing_price_list.id)
            self.assertIn('already exists', result['message'])
            
        finally:
            # Restore original method
            self.pos_order_model.get_pricing_scenarios = original_method

    def test_apply_pricing_scenarios_invalid_scenario(self):
        """Test applying pricing scenarios with invalid scenario"""
        result = self.pos_order_model.apply_pricing_scenarios(
            month='2024-01',
            scenario='invalid_scenario',
            mode='uniform',
            dry_run=True
        )
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('Invalid scenario type', result['message'])

    def test_apply_pricing_scenarios_custom_target_required(self):
        """Test that custom target is required for custom scenarios"""
        result = self.pos_order_model.apply_pricing_scenarios(
            month='2024-01',
            scenario='net_custom',
            mode='uniform',
            dry_run=True
        )
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('Target amount is required', result['message'])

    def test_price_list_activation(self):
        """Test price list activation"""
        # Create test price list
        price_list = self.price_list_model.create({
            'name': 'Test Price List',
            'month_key': '2024-01',
            'source_scenario': 'net_10k',
            'mode': 'uniform',
            'target': 10000,
            'status': 'draft'
        })
        
        # Create test price list item
        self.price_list_item_model.create({
            'price_list_id': price_list.id,
            'product_name': 'Product A',
            'old_price': 100.0,
            'new_price': 198.5,
            'pct_change': 0.985,
            'floor_applied': False
        })
        
        # Test activation
        result = price_list.action_activate()
        
        # Check that price list was activated
        self.assertEqual(price_list.status, 'active')
        self.assertEqual(price_list.activated_by, self.env.user)
        self.assertIsNotNone(price_list.activated_at)
        
        # Check that product price was updated
        self.product_a.refresh()
        self.assertEqual(self.product_a.list_price, 198.5)

    def test_price_list_activation_permissions(self):
        """Test that only pricing admins can activate price lists"""
        # Create test price list
        price_list = self.price_list_model.create({
            'name': 'Test Price List',
            'month_key': '2024-01',
            'source_scenario': 'net_10k',
            'mode': 'uniform',
            'target': 10000,
            'status': 'draft'
        })
        
        # Test activation without proper permissions
        with self.assertRaises(UserError):
            price_list.action_activate()

    def test_price_list_activation_wrong_status(self):
        """Test that only draft price lists can be activated"""
        # Create test price list with active status
        price_list = self.price_list_model.create({
            'name': 'Test Price List',
            'month_key': '2024-01',
            'source_scenario': 'net_10k',
            'mode': 'uniform',
            'target': 10000,
            'status': 'active'
        })
        
        # Test activation of already active price list
        with self.assertRaises(UserError):
            price_list.action_activate()

    def test_price_list_item_validation(self):
        """Test price list item validation"""
        # Create test price list
        price_list = self.price_list_model.create({
            'name': 'Test Price List',
            'month_key': '2024-01',
            'source_scenario': 'net_10k',
            'mode': 'uniform',
            'target': 10000,
            'status': 'draft'
        })
        
        # Test creating item with negative price
        with self.assertRaises(Exception):  # ValidationError
            self.price_list_item_model.create({
                'price_list_id': price_list.id,
                'product_name': 'Product A',
                'old_price': 100.0,
                'new_price': -50.0,  # Invalid negative price
                'pct_change': -1.5,
                'floor_applied': False
            })
