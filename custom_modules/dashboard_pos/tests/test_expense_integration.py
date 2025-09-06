# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from datetime import date, datetime
import logging

_logger = logging.getLogger(__name__)


class TestExpenseIntegration(TransactionCase):
    """Test expense integration functionality"""

    def setUp(self):
        super().setUp()
        self.pos_order_model = self.env['pos.order']
        self.account_model = self.env['account.account']
        self.move_model = self.env['account.move']
        self.move_line_model = self.env['account.move.line']
        
        # Create test company
        self.company = self.env.company
        
        # Create test accounts
        self.expense_account = self.account_model.create({
            'name': 'Test Expense Account',
            'code': '6000',
            'account_type': 'expense',
            'company_id': self.company.id
        })
        
        self.cogs_account = self.account_model.create({
            'name': 'Test COGS Account',
            'code': '4000',
            'account_type': 'expense',
            'company_id': self.company.id
        })
        
        self.vat_account = self.account_model.create({
            'name': 'Test VAT Account',
            'code': '5000',
            'account_type': 'liability',
            'company_id': self.company.id
        })

    def test_get_monthly_expenses_with_data(self):
        """Test getting monthly expenses when data exists"""
        # Create test date range
        month_start = date(2024, 1, 1)
        month_end = date(2024, 2, 1)
        
        # Create test journal entry with expenses
        move = self.move_model.create({
            'date': date(2024, 1, 15),
            'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1).id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.expense_account.id,
                    'debit': 1000.0,
                    'credit': 0.0,
                }),
                (0, 0, {
                    'account_id': self.env['account.account'].search([('account_type', '=', 'asset')], limit=1).id,
                    'debit': 0.0,
                    'credit': 1000.0,
                })
            ]
        })
        move.action_post()
        
        # Test expense calculation
        expenses = self.pos_order_model._get_monthly_expenses(month_start, month_end)
        
        # Should return 1000.0 (the expense amount)
        self.assertEqual(expenses, 1000.0)

    def test_get_monthly_expenses_excludes_cogs(self):
        """Test that COGS accounts are excluded from expenses"""
        # Create test date range
        month_start = date(2024, 1, 1)
        month_end = date(2024, 2, 1)
        
        # Create test journal entry with COGS
        move = self.move_model.create({
            'date': date(2024, 1, 15),
            'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1).id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.cogs_account.id,
                    'debit': 500.0,
                    'credit': 0.0,
                }),
                (0, 0, {
                    'account_id': self.env['account.account'].search([('account_type', '=', 'asset')], limit=1).id,
                    'debit': 0.0,
                    'credit': 500.0,
                })
            ]
        })
        move.action_post()
        
        # Test expense calculation
        expenses = self.pos_order_model._get_monthly_expenses(month_start, month_end)
        
        # Should return 0.0 (COGS excluded)
        self.assertEqual(expenses, 0.0)

    def test_get_monthly_expenses_excludes_vat(self):
        """Test that VAT accounts are excluded from expenses"""
        # Create test date range
        month_start = date(2024, 1, 1)
        month_end = date(2024, 2, 1)
        
        # Create test journal entry with VAT
        move = self.move_model.create({
            'date': date(2024, 1, 15),
            'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1).id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.vat_account.id,
                    'debit': 50.0,
                    'credit': 0.0,
                }),
                (0, 0, {
                    'account_id': self.env['account.account'].search([('account_type', '=', 'asset')], limit=1).id,
                    'debit': 0.0,
                    'credit': 50.0,
                })
            ]
        })
        move.action_post()
        
        # Test expense calculation
        expenses = self.pos_order_model._get_monthly_expenses(month_start, month_end)
        
        # Should return 0.0 (VAT excluded)
        self.assertEqual(expenses, 0.0)

    def test_get_monthly_expenses_no_data(self):
        """Test getting monthly expenses when no data exists"""
        # Create test date range
        month_start = date(2024, 1, 1)
        month_end = date(2024, 2, 1)
        
        # Test expense calculation with no data
        expenses = self.pos_order_model._get_monthly_expenses(month_start, month_end)
        
        # Should return 0.0
        self.assertEqual(expenses, 0.0)

    def test_check_expenses_available_with_data(self):
        """Test checking if expenses are available when data exists"""
        # Create test date range
        month_start = date(2024, 1, 1)
        month_end = date(2024, 2, 1)
        
        # Create test journal entry
        move = self.move_model.create({
            'date': date(2024, 1, 15),
            'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1).id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.expense_account.id,
                    'debit': 1000.0,
                    'credit': 0.0,
                }),
                (0, 0, {
                    'account_id': self.env['account.account'].search([('account_type', '=', 'asset')], limit=1).id,
                    'debit': 0.0,
                    'credit': 1000.0,
                })
            ]
        })
        move.action_post()
        
        # Test availability check
        available = self.pos_order_model._check_expenses_available(month_start, month_end)
        
        # Should return True
        self.assertTrue(available)

    def test_check_expenses_available_no_data(self):
        """Test checking if expenses are available when no data exists"""
        # Create test date range
        month_start = date(2024, 1, 1)
        month_end = date(2024, 2, 1)
        
        # Test availability check with no data
        available = self.pos_order_model._check_expenses_available(month_start, month_end)
        
        # Should return False
        self.assertFalse(available)

    def test_negative_expenses_clamped(self):
        """Test that negative expenses are clamped to 0"""
        # Create test date range
        month_start = date(2024, 1, 1)
        month_end = date(2024, 2, 1)
        
        # Create test journal entry with negative expense (credit)
        move = self.move_model.create({
            'date': date(2024, 1, 15),
            'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1).id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.expense_account.id,
                    'debit': 0.0,
                    'credit': 100.0,  # Negative expense
                }),
                (0, 0, {
                    'account_id': self.env['account.account'].search([('account_type', '=', 'asset')], limit=1).id,
                    'debit': 100.0,
                    'credit': 0.0,
                })
            ]
        })
        move.action_post()
        
        # Test expense calculation
        expenses = self.pos_order_model._get_monthly_expenses(month_start, month_end)
        
        # Should return 0.0 (clamped from -100.0)
        self.assertEqual(expenses, 0.0)
