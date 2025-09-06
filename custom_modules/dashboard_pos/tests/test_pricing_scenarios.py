# -*- coding: utf-8 -*-
import unittest
from unittest.mock import Mock, patch
from datetime import date, datetime
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestPricingScenarios(TransactionCase):
    """Test cases for pricing scenarios calculations"""

    def setUp(self):
        super().setUp()
        self.pos_order_model = self.env['pos.order']
        
        # Sample product data for testing
        self.sample_product_data = [
            {
                'product_name': 'Product A',
                'qty': 50.0,
                'price': 100.0,
                'cost': 80.0
            },
            {
                'product_name': 'Product B',
                'qty': 40.0,
                'price': 80.0,
                'cost': 60.0
            },
            {
                'product_name': 'Product C',
                'qty': 30.0,
                'price': 60.0,
                'cost': 55.0
            }
        ]
        
        # Sample expenses
        self.sample_expenses = 1800.0

    def test_calculate_totals(self):
        """Test calculation of R, G, E, N totals"""
        # Calculate expected values
        expected_R = sum(item['qty'] * item['price'] for item in self.sample_product_data)
        expected_G = sum(item['qty'] * (item['price'] - item['cost']) for item in self.sample_product_data)
        expected_N = expected_G - self.sample_expenses
        
        # Calculate minimum cost-floor uplift
        expected_x_min = 0
        for item in self.sample_product_data:
            if item['price'] > 0:
                cost_floor = (item['cost'] / item['price']) - 1
                expected_x_min = max(expected_x_min, cost_floor)
        
        # Call the method
        totals = self.pos_order_model._calculate_totals(self.sample_product_data)
        
        # Assertions
        self.assertEqual(totals['R'], round(expected_R, 2))
        self.assertEqual(totals['G'], round(expected_G, 2))
        self.assertEqual(totals['E'], round(self.sample_expenses, 2))
        self.assertEqual(totals['N'], round(expected_N, 2))
        self.assertEqual(totals['x_min'], round(expected_x_min, 4))

    def test_calculate_break_even(self):
        """Test break-even price calculations"""
        totals = {
            'R': 12200.0,  # 50*100 + 40*80 + 30*60
            'G': 2200.0,   # 50*20 + 40*20 + 30*5
            'E': 1800.0,
            'N': 400.0,
            'x_min': 0.0
        }
        
        break_even_data = self.pos_order_model._calculate_break_even(self.sample_product_data, totals)
        
        # Check that we have data for all products
        self.assertEqual(len(break_even_data), 3)
        
        # Check first product break-even calculation
        first_product = break_even_data[0]
        expected_price_be = 80.0 + (1800.0 * 100.0 / 12200.0)  # cost + (E * price / R)
        self.assertEqual(first_product['price_target'], round(expected_price_be, 2))
        self.assertEqual(first_product['product'], 'Product A')
        self.assertEqual(first_product['qty'], 50.0)

    def test_calculate_uniform_uplift(self):
        """Test uniform uplift calculations"""
        x = 0.1  # 10% uplift
        
        uniform_data = self.pos_order_model._calculate_uniform_uplift(self.sample_product_data, x)
        
        # Check that we have data for all products
        self.assertEqual(len(uniform_data), 3)
        
        # Check first product uniform calculation
        first_product = uniform_data[0]
        expected_price_target = 100.0 * (1 + 0.1)  # price * (1 + x)
        expected_margin_after = ((expected_price_target - 80.0) / expected_price_target) * 100
        
        self.assertEqual(first_product['price_target'], round(expected_price_target, 2))
        self.assertEqual(first_product['pct'], 10.0)  # x * 100
        self.assertEqual(first_product['margin_after'], round(expected_margin_after, 2))

    def test_calculate_weighted_uplift(self):
        """Test weighted uplift calculations"""
        totals = {
            'R': 12200.0,
            'G': 2200.0,
            'E': 1800.0,
            'N': 400.0,
            'x_min': 0.0
        }
        x_budget = 0.1  # 10% uplift budget
        
        weighted_data = self.pos_order_model._calculate_weighted_uplift(self.sample_product_data, totals, x_budget)
        
        # Check that we have data for all products
        self.assertEqual(len(weighted_data), 3)
        
        # Check that all target prices are above cost
        for product in weighted_data:
            self.assertGreaterEqual(product['price_target'], product['cost'])

    def test_check_unrealistic_scenarios(self):
        """Test unrealistic scenario detection"""
        totals = {
            'R': 12200.0,
            'G': 2200.0,
            'E': 1800.0,
            'N': 400.0,
            'x_min': 0.0
        }
        
        # Test 30% threshold
        x_raw_high = 0.35  # 35% uplift
        unrealistic_high = self.pos_order_model._check_unrealistic(x_raw_high, self.sample_product_data, totals, 10000)
        self.assertTrue(unrealistic_high)
        
        # Test normal scenario
        x_raw_normal = 0.1  # 10% uplift
        unrealistic_normal = self.pos_order_model._check_unrealistic(x_raw_normal, self.sample_product_data, totals, 10000)
        self.assertFalse(unrealistic_normal)

    def test_calculate_net_target(self):
        """Test net target scenario calculations"""
        totals = {
            'R': 12200.0,
            'G': 2200.0,
            'E': 1800.0,
            'N': 400.0,
            'x_min': 0.0
        }
        target_net = 10000.0
        
        net_target_data = self.pos_order_model._calculate_net_target(self.sample_product_data, totals, target_net)
        
        # Check that we have both uniform and weighted data
        self.assertIn('uniform', net_target_data)
        self.assertIn('weighted', net_target_data)
        
        # Check uniform data
        uniform = net_target_data['uniform']
        self.assertIn('x', uniform)
        self.assertIn('rows', uniform)
        self.assertIn('unrealistic', uniform)
        
        # Check weighted data
        weighted = net_target_data['weighted']
        self.assertIn('x_budget', weighted)
        self.assertIn('x_range', weighted)
        self.assertIn('rows', weighted)
        self.assertIn('unrealistic', weighted)

    def test_calculate_custom_net_scenario(self):
        """Test custom net scenario calculation"""
        # Mock the get_pricing_scenarios method to return sample data
        with patch.object(self.pos_order_model, 'get_pricing_scenarios') as mock_get_scenarios:
            mock_get_scenarios.return_value = {
                'status': 'ok',
                'totals': {
                    'R': 12200.0,
                    'G': 2200.0,
                    'E': 1800.0,
                    'N': 400.0,
                    'x_min': 0.0
                }
            }
            
            with patch.object(self.pos_order_model, '_get_monthly_product_data') as mock_get_data:
                mock_get_data.return_value = self.sample_product_data
                
                result = self.pos_order_model.calculate_custom_net_scenario('2024-01', 25000)
                
                # Check that the result has the expected structure
                self.assertEqual(result['status'], 'ok')
                self.assertEqual(result['month'], '2024-01')
                self.assertIn('scenarios', result)
                self.assertIn('net_custom', result['scenarios'])

    def test_insufficient_sales_scenario(self):
        """Test handling of insufficient sales data"""
        # Test with empty product data
        empty_data = []
        result = self.pos_order_model._calculate_totals(empty_data)
        
        # Should handle empty data gracefully
        self.assertEqual(result['R'], 0.0)
        self.assertEqual(result['G'], 0.0)
        self.assertEqual(result['x_min'], 0.0)

    def test_cost_floor_enforcement(self):
        """Test that cost floors are properly enforced"""
        # Create product data where cost is higher than price
        problematic_data = [
            {
                'product_name': 'Problem Product',
                'qty': 10.0,
                'price': 50.0,
                'cost': 80.0  # Cost higher than price
            }
        ]
        
        totals = {
            'R': 500.0,
            'G': -300.0,  # Negative gross profit
            'E': 100.0,
            'N': -400.0,
            'x_min': 0.6  # 60% minimum uplift needed
        }
        
        # Test uniform uplift with cost floor
        uniform_data = self.pos_order_model._calculate_uniform_uplift(problematic_data, 0.1)  # 10% uplift
        # The actual uplift should be adjusted to meet cost floor
        
        # Test weighted uplift with cost floor
        weighted_data = self.pos_order_model._calculate_weighted_uplift(problematic_data, totals, 0.1)
        
        # Both should ensure target price >= cost
        for product in uniform_data + weighted_data:
            self.assertGreaterEqual(product['price_target'], product['cost'])

    def test_precision_and_rounding(self):
        """Test that calculations maintain proper precision and rounding"""
        totals = {
            'R': 12200.0,
            'G': 2200.0,
            'E': 1800.0,
            'N': 400.0,
            'x_min': 0.0
        }
        
        break_even_data = self.pos_order_model._calculate_break_even(self.sample_product_data, totals)
        
        # Check that all monetary values are rounded to 2 decimal places
        for product in break_even_data:
            self.assertEqual(len(str(product['price_target']).split('.')[-1]), 2)
            self.assertEqual(len(str(product['diff']).split('.')[-1]), 2)
            self.assertEqual(len(str(product['diff_pct']).split('.')[-1]), 2)

    def test_validation_checks(self):
        """Test various validation scenarios"""
        # Test with zero revenue
        zero_revenue_data = [
            {
                'product_name': 'Zero Revenue Product',
                'qty': 0.0,
                'price': 100.0,
                'cost': 80.0
            }
        ]
        
        totals = self.pos_order_model._calculate_totals(zero_revenue_data)
        self.assertEqual(totals['R'], 0.0)
        
        # Test break-even with zero revenue
        break_even_data = self.pos_order_model._calculate_break_even(zero_revenue_data, totals)
        self.assertEqual(len(break_even_data), 0)  # Should return empty list


if __name__ == '__main__':
    unittest.main()
