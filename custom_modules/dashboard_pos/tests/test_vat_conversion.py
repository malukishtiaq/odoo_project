# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class TestVATConversion(TransactionCase):
    """Test VAT conversion functionality"""

    def setUp(self):
        super().setUp()
        self.pos_order_model = self.env['pos.order']
        self.product_template_model = self.env['product.template']
        self.tax_model = self.env['account.tax']
        
        # Create test company
        self.company = self.env.company
        
        # Create test VAT tax
        self.vat_tax = self.tax_model.create({
            'name': 'UAE VAT 5%',
            'amount': 5.0,
            'amount_type': 'percent',
            'type_tax_use': 'sale',
            'company_id': self.company.id
        })
        
        # Create test product with VAT
        self.product_with_vat = self.product_template_model.create({
            'name': 'Product with VAT',
            'available_in_pos': True,
            'taxes_id': [(6, 0, [self.vat_tax.id])],
            'company_id': self.company.id
        })
        
        # Create test product without VAT
        self.product_without_vat = self.product_template_model.create({
            'name': 'Product without VAT',
            'available_in_pos': True,
            'taxes_id': [(6, 0, [])],
            'company_id': self.company.id
        })

    def test_get_product_vat_rate_with_vat(self):
        """Test getting VAT rate for product with VAT"""
        vat_rate = self.pos_order_model._get_product_vat_rate('Product with VAT')
        
        # Should return 0.05 (5% VAT)
        self.assertEqual(vat_rate, 0.05)

    def test_get_product_vat_rate_without_vat(self):
        """Test getting VAT rate for product without VAT"""
        vat_rate = self.pos_order_model._get_product_vat_rate('Product without VAT')
        
        # Should return default 0.05 (UAE VAT rate)
        self.assertEqual(vat_rate, 0.05)

    def test_get_product_vat_rate_nonexistent(self):
        """Test getting VAT rate for nonexistent product"""
        vat_rate = self.pos_order_model._get_product_vat_rate('Nonexistent Product')
        
        # Should return default 0.05 (UAE VAT rate)
        self.assertEqual(vat_rate, 0.05)

    def test_convert_to_net_prices_with_vat(self):
        """Test converting gross prices to net prices with VAT"""
        raw_data = [
            {
                'product_name': 'Product with VAT',
                'qty': 10.0,
                'price': 105.0,  # Gross price (105 AED)
                'cost': 84.0     # Gross cost (84 AED)
            }
        ]
        
        converted_data = self.pos_order_model._convert_to_net_prices(raw_data)
        
        # Price should be 100.0 (105 / 1.05)
        # Cost should be 80.0 (84 / 1.05)
        self.assertEqual(converted_data[0]['price'], 100.0)
        self.assertEqual(converted_data[0]['cost'], 80.0)

    def test_convert_to_net_prices_without_vat(self):
        """Test converting prices when no VAT is applied"""
        raw_data = [
            {
                'product_name': 'Product without VAT',
                'qty': 10.0,
                'price': 100.0,  # Already net price
                'cost': 80.0     # Already net cost
            }
        ]
        
        converted_data = self.pos_order_model._convert_to_net_prices(raw_data)
        
        # Prices should remain the same (no VAT conversion)
        self.assertEqual(converted_data[0]['price'], 100.0)
        self.assertEqual(converted_data[0]['cost'], 80.0)

    def test_convert_to_net_prices_zero_prices(self):
        """Test converting prices when prices are zero"""
        raw_data = [
            {
                'product_name': 'Product with zero prices',
                'qty': 10.0,
                'price': 0.0,
                'cost': 0.0
            }
        ]
        
        converted_data = self.pos_order_model._convert_to_net_prices(raw_data)
        
        # Prices should remain zero
        self.assertEqual(converted_data[0]['price'], 0.0)
        self.assertEqual(converted_data[0]['cost'], 0.0)

    def test_convert_to_net_prices_mixed_products(self):
        """Test converting prices for multiple products with different VAT rates"""
        raw_data = [
            {
                'product_name': 'Product with VAT',
                'qty': 10.0,
                'price': 105.0,  # Gross price
                'cost': 84.0     # Gross cost
            },
            {
                'product_name': 'Product without VAT',
                'qty': 5.0,
                'price': 100.0,  # Net price
                'cost': 80.0     # Net cost
            }
        ]
        
        converted_data = self.pos_order_model._convert_to_net_prices(raw_data)
        
        # First product: 105 -> 100, 84 -> 80
        self.assertEqual(converted_data[0]['price'], 100.0)
        self.assertEqual(converted_data[0]['cost'], 80.0)
        
        # Second product: prices remain the same
        self.assertEqual(converted_data[1]['price'], 100.0)
        self.assertEqual(converted_data[1]['cost'], 80.0)

    def test_vat_conversion_precision(self):
        """Test VAT conversion maintains proper precision"""
        raw_data = [
            {
                'product_name': 'Product with VAT',
                'qty': 1.0,
                'price': 105.25,  # Gross price with cents
                'cost': 84.20     # Gross cost with cents
            }
        ]
        
        converted_data = self.pos_order_model._convert_to_net_prices(raw_data)
        
        # Price should be 100.238... rounded to 2 decimals
        # Cost should be 80.190... rounded to 2 decimals
        self.assertAlmostEqual(converted_data[0]['price'], 100.24, places=2)
        self.assertAlmostEqual(converted_data[0]['cost'], 80.19, places=2)
