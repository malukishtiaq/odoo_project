# -*- coding: utf-8 -*-
"""
Unit tests for comprehensive monthly sales data functionality
"""

import unittest
from datetime import date, timedelta
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestComprehensiveSalesData(TransactionCase):
    """Test cases for comprehensive monthly sales data methods"""

    def setUp(self):
        super().setUp()
        self.pos_order_model = self.env['pos.order']
        
        # Create test dates
        self.month_start = date.today().replace(day=1)
        self.month_end = (self.month_start + timedelta(days=32)).replace(day=1)
        
        # Create test company
        self.company = self.env.company

    def test_get_complete_monthly_sales_data_structure(self):
        """Test the structure of comprehensive monthly sales data"""
        result = self.pos_order_model.get_complete_monthly_sales_data(
            self.month_start, self.month_end
        )
        
        # Validate structure
        self.assertIsInstance(result, dict)
        self.assertIn('month_start', result)
        self.assertIn('month_end', result)
        self.assertIn('total_products', result)
        self.assertIn('total_revenue', result)
        self.assertIn('total_quantity', result)
        self.assertIn('products', result)
        
        # Validate data types
        self.assertIsInstance(result['total_products'], int)
        self.assertIsInstance(result['total_revenue'], (int, float))
        self.assertIsInstance(result['total_quantity'], (int, float))
        self.assertIsInstance(result['products'], list)

    def test_get_complete_monthly_sales_data_calculations(self):
        """Test data accuracy and calculations"""
        result = self.pos_order_model.get_complete_monthly_sales_data(
            self.month_start, self.month_end
        )
        
        # Validate calculations
        calculated_total_revenue = sum(p['total_revenue'] for p in result['products'])
        calculated_total_quantity = sum(p['total_quantity'] for p in result['products'])
        
        self.assertAlmostEqual(result['total_revenue'], calculated_total_revenue, places=2)
        self.assertAlmostEqual(result['total_quantity'], calculated_total_quantity, places=2)
        
        # Validate margin calculations for each product
        for product in result['products']:
            expected_margin = product['total_revenue'] - product['total_cost']
            self.assertAlmostEqual(product['margin_amount'], expected_margin, places=2)
            
            if product['total_revenue'] > 0:
                expected_margin_pct = (expected_margin / product['total_revenue']) * 100
                self.assertAlmostEqual(product['margin_percentage'], expected_margin_pct, places=2)

    def test_get_all_data_backward_compatibility(self):
        """Test that updated get_all_data method maintains backward compatibility"""
        result = self.pos_order_model.get_all_data(
            self.month_start.strftime('%Y-%m-%d'),
            self.month_end.strftime('%Y-%m-%d')
        )
        
        # Validate backward compatibility
        self.assertIn('top_selling_product_pos', result)
        self.assertIn('top_selling_product_inv', result)
        self.assertIn('low_selling_product_pos', result)
        self.assertIn('low_selling_product_inv', result)
        self.assertIn('payment_details', result)
        self.assertIn('complete_data', result)
        
        # Validate data structure
        self.assertIsInstance(result['top_selling_product_pos'], list)
        self.assertIsInstance(result['top_selling_product_inv'], list)
        self.assertIsInstance(result['low_selling_product_pos'], list)
        self.assertIsInstance(result['low_selling_product_inv'], list)
        self.assertIsInstance(result['complete_data'], dict)

    def test_get_product_performance_analysis(self):
        """Test product performance analysis method"""
        result = self.pos_order_model.get_product_performance_analysis(
            self.month_start, self.month_end
        )
        
        # Validate structure
        self.assertIn('summary', result)
        self.assertIn('high_performers', result)
        self.assertIn('medium_performers', result)
        self.assertIn('low_performers', result)
        
        # Validate summary
        summary = result['summary']
        self.assertIn('total_products', summary)
        self.assertIn('total_revenue', summary)
        self.assertIn('high_performers_count', summary)
        self.assertIn('medium_performers_count', summary)
        self.assertIn('low_performers_count', summary)
        
        # Validate counts
        total_count = (summary['high_performers_count'] + 
                      summary['medium_performers_count'] + 
                      summary['low_performers_count'])
        self.assertEqual(summary['total_products'], total_count)

    def test_get_category_analysis(self):
        """Test category analysis method"""
        result = self.pos_order_model.get_category_analysis(
            self.month_start, self.month_end
        )
        
        # Validate structure
        self.assertIsInstance(result, list)
        
        if result:  # Only test if there are categories
            for category in result:
                self.assertIn('category_name', category)
                self.assertIn('product_count', category)
                self.assertIn('total_quantity', category)
                self.assertIn('total_revenue', category)
                self.assertIn('total_cost', category)
                self.assertIn('margin_amount', category)
                self.assertIn('revenue_share', category)
                self.assertIn('margin_percentage', category)
                self.assertIn('products', category)

    def test_export_monthly_sales_data_csv(self):
        """Test CSV export functionality"""
        try:
            result = self.pos_order_model.export_monthly_sales_data(
                self.month_start, self.month_end, 'csv'
            )
            
            # Validate CSV format
            self.assertIsInstance(result, str)
            self.assertIn(',', result)  # Should contain commas for CSV format
            self.assertIn('Product Name', result)  # Should contain headers
            
        except Exception as e:
            # If no data available, that's okay for testing
            self.assertIn('No data', str(e))

    def test_export_monthly_sales_data_json(self):
        """Test JSON export functionality"""
        try:
            result = self.pos_order_model.export_monthly_sales_data(
                self.month_start, self.month_end, 'json'
            )
            
            # Validate JSON format
            self.assertIsInstance(result, str)
            self.assertIn('{', result)  # Should start with JSON object
            self.assertIn('"products"', result)  # Should contain products key
            
        except Exception as e:
            # If no data available, that's okay for testing
            self.assertIn('No data', str(e))

    def test_date_validation(self):
        """Test date validation and error handling"""
        # Test with invalid date format
        with self.assertRaises(Exception):
            self.pos_order_model.get_complete_monthly_sales_data(
                'invalid-date', 'invalid-date'
            )

    def test_empty_data_handling(self):
        """Test handling of empty data scenarios"""
        # Test with future dates (should return empty data)
        future_start = date.today() + timedelta(days=365)
        future_end = future_start + timedelta(days=32)
        
        result = self.pos_order_model.get_complete_monthly_sales_data(
            future_start, future_end
        )
        
        # Should return empty but valid structure
        self.assertEqual(result['total_products'], 0)
        self.assertEqual(result['total_revenue'], 0)
        self.assertEqual(result['total_quantity'], 0)
        self.assertEqual(len(result['products']), 0)

    def test_data_consistency(self):
        """Test data consistency between methods"""
        # Get data from comprehensive method
        comprehensive_data = self.pos_order_model.get_complete_monthly_sales_data(
            self.month_start, self.month_end
        )
        
        # Get data from updated get_all_data method
        all_data = self.pos_order_model.get_all_data(
            self.month_start.strftime('%Y-%m-%d'),
            self.month_end.strftime('%Y-%m-%d')
        )
        
        # The complete_data in get_all_data should match comprehensive_data
        self.assertEqual(
            comprehensive_data['total_products'],
            all_data['complete_data']['total_products']
        )
        self.assertEqual(
            comprehensive_data['total_revenue'],
            all_data['complete_data']['total_revenue']
        )

    def test_performance_metrics(self):
        """Test performance-related calculations"""
        result = self.pos_order_model.get_complete_monthly_sales_data(
            self.month_start, self.month_end
        )
        
        for product in result['products']:
            # Test turnover ratio calculation
            if product['current_stock'] > 0:
                expected_turnover = product['total_quantity'] / product['current_stock']
                self.assertAlmostEqual(product['turnover_ratio'], expected_turnover, places=2)
            
            # Test average daily sales calculation
            if product['days_sold'] > 0:
                expected_daily_sales = product['total_quantity'] / product['days_sold']
                self.assertAlmostEqual(product['avg_daily_sales'], expected_daily_sales, places=2)
            
            # Test price consistency
            if product['min_price'] == product['max_price']:
                self.assertEqual(product['price_consistency'], 'consistent')
            else:
                self.assertEqual(product['price_consistency'], 'variable')


if __name__ == '__main__':
    unittest.main()
