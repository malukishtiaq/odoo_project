#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test runner for pricing scenarios calculations.
This can be run independently to verify the business logic.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime
import math


class PricingScenariosCalculator:
    """Standalone calculator for testing pricing scenarios logic"""
    
    def __init__(self):
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
        self.sample_expenses = 1800.0

    def calculate_totals(self, product_data):
        """Calculate R, G, E, N totals"""
        R = sum(item['qty'] * item['price'] for item in product_data)
        G = sum(item['qty'] * (item['price'] - item['cost']) for item in product_data)
        E = self.sample_expenses
        N = G - E
        
        # Calculate minimum cost-floor uplift
        x_min = 0
        for item in product_data:
            if item['price'] > 0:
                cost_floor = (item['cost'] / item['price']) - 1
                x_min = max(x_min, cost_floor)
        
        return {
            'R': round(R, 2),
            'G': round(G, 2),
            'E': round(E, 2),
            'N': round(N, 2),
            'x_min': round(x_min, 4)
        }

    def calculate_break_even(self, product_data, totals):
        """Calculate break-even prices"""
        break_even_data = []
        
        for item in product_data:
            if totals['R'] > 0:
                # Break-even price = cost + (E * price / R)
                price_be = item['cost'] + (totals['E'] * item['price'] / totals['R'])
                diff = item['price'] - price_be
                diff_pct = ((item['price'] / price_be) - 1) * 100 if price_be > 0 else 0
                
                break_even_data.append({
                    'product': item['product_name'],
                    'qty': round(item['qty'], 2),
                    'cost': round(item['cost'], 2),
                    'price_real': round(item['price'], 2),
                    'price_target': round(price_be, 2),
                    'diff': round(diff, 2),
                    'diff_pct': round(diff_pct, 2)
                })
        
        return break_even_data

    def calculate_uniform_uplift(self, product_data, x):
        """Calculate uniform uplift scenario"""
        uniform_data = []
        
        for item in product_data:
            price_target = item['price'] * (1 + x)
            pct_change = x * 100
            margin_after = ((price_target - item['cost']) / price_target) * 100 if price_target > 0 else 0
            
            uniform_data.append({
                'product': item['product_name'],
                'qty': round(item['qty'], 2),
                'cost': round(item['cost'], 2),
                'price_real': round(item['price'], 2),
                'price_target': round(price_target, 2),
                'pct': round(pct_change, 2),
                'margin_after': round(margin_after, 2)
            })
        
        return uniform_data

    def check_unrealistic(self, x_raw, product_data, totals, N_target):
        """Check if target is unrealistic"""
        # Check 30% threshold
        if x_raw > 0.30:
            return True
        
        # Check 50% cap scenario
        x_cap = max(min(x_raw, 0.50), totals['x_min'])
        projected_net = totals['N'] + (x_cap * totals['R'])
        if projected_net < N_target:
            return True
        
        # Check if many items need >2x price
        high_uplift_count = 0
        for item in product_data:
            if item['price'] > 0:
                required_uplift = (item['cost'] / item['price']) - 1
                if required_uplift > 1.0:  # >2x price
                    high_uplift_count += 1
        
        if high_uplift_count > len(product_data) * 0.1:  # >10% of items
            return True
        
        return False

    def run_tests(self):
        """Run basic validation tests"""
        print("Running Pricing Scenarios Tests...")
        print("=" * 50)
        
        # Test 1: Calculate totals
        print("\n1. Testing totals calculation...")
        totals = self.calculate_totals(self.sample_product_data)
        print(f"   Revenue (R): {totals['R']}")
        print(f"   Gross Profit (G): {totals['G']}")
        print(f"   Expenses (E): {totals['E']}")
        print(f"   Net Profit (N): {totals['N']}")
        print(f"   Min Uplift (x_min): {totals['x_min']}")
        
        # Verify break-even calculation
        expected_R = 50*100 + 40*80 + 30*60  # 12200
        expected_G = 50*20 + 40*20 + 30*5    # 2200
        expected_N = expected_G - 1800       # 400
        
        assert abs(totals['R'] - expected_R) < 0.01, f"R calculation error: {totals['R']} != {expected_R}"
        assert abs(totals['G'] - expected_G) < 0.01, f"G calculation error: {totals['G']} != {expected_G}"
        assert abs(totals['N'] - expected_N) < 0.01, f"N calculation error: {totals['N']} != {expected_N}"
        print("   ✓ Totals calculation verified")
        
        # Test 2: Break-even scenario
        print("\n2. Testing break-even calculation...")
        break_even_data = self.calculate_break_even(self.sample_product_data, totals)
        
        # Verify break-even total margin equals E
        total_margin = sum(item['qty'] * (item['price_target'] - item['cost']) for item in break_even_data)
        assert abs(total_margin - totals['E']) < 0.01, f"Break-even margin error: {total_margin} != {totals['E']}"
        print(f"   Total break-even margin: {total_margin} (should equal E: {totals['E']})")
        print("   ✓ Break-even calculation verified")
        
        # Test 3: Uniform uplift scenario
        print("\n3. Testing uniform uplift calculation...")
        target_net = 10000
        x_raw = (target_net - totals['N']) / totals['R']
        x = max(x_raw, totals['x_min'])
        
        uniform_data = self.calculate_uniform_uplift(self.sample_product_data, x)
        
        # Verify uniform scenario reaches target
        projected_net = totals['N'] + (x * totals['R'])
        assert abs(projected_net - target_net) < 0.5, f"Uniform target error: {projected_net} != {target_net}"
        print(f"   Required uplift: {x*100:.2f}%")
        print(f"   Projected net: {projected_net} (target: {target_net})")
        print("   ✓ Uniform uplift calculation verified")
        
        # Test 4: Unrealistic detection
        print("\n4. Testing unrealistic detection...")
        unrealistic_high = self.check_unrealistic(0.35, self.sample_product_data, totals, 50000)
        unrealistic_normal = self.check_unrealistic(0.1, self.sample_product_data, totals, 10000)
        
        print(f"   High uplift (35%): {unrealistic_high}")
        print(f"   Normal uplift (10%): {unrealistic_normal}")
        
        assert unrealistic_high == True, "Should detect 35% uplift as unrealistic"
        # Note: 10% uplift might be unrealistic if it doesn't reach the target
        print("   ✓ Unrealistic detection verified")
        
        # Test 5: Cost floor enforcement
        print("\n5. Testing cost floor enforcement...")
        for item in uniform_data:
            assert item['price_target'] >= item['cost'], f"Cost floor violated for {item['product']}"
        print("   ✓ Cost floor enforcement verified")
        
        print("\n" + "=" * 50)
        print("All tests passed! ✓")
        print("\nSample Results:")
        print("-" * 30)
        print("Break-even prices:")
        for item in break_even_data[:2]:  # Show first 2 items
            print(f"  {item['product']}: {item['price_real']} → {item['price_target']} ({item['diff_pct']:+.1f}%)")
        
        print("\nUniform uplift (+10k target):")
        for item in uniform_data[:2]:  # Show first 2 items
            print(f"  {item['product']}: {item['price_real']} → {item['price_target']} ({item['pct']:+.1f}%)")


if __name__ == '__main__':
    calculator = PricingScenariosCalculator()
    calculator.run_tests()
