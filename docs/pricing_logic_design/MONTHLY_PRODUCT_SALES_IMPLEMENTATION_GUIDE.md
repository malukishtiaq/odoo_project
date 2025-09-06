# Monthly Product Sales Data Implementation Guide

## Problem Statement
The current POS dashboard implementation has limitations in retrieving complete monthly product sales data. The existing methods only return top 5-10 products and have issues with data aggregation and price handling. This guide provides a comprehensive solution to get all products sold in one month with their prices and quantities.

## Current Issues Analysis

### 1. Existing Method Problems

#### A. `get_all_data()` Method Issues
**Location**: `custom_modules/dashboard_pos/models/pos_order.py` lines 82-199

**Problems**:
- Uses `LIMIT 5` - only returns top 5 products
- Groups by `price_unit` - creates separate rows for same product at different prices
- No comprehensive data aggregation
- Missing important fields like costs, margins, categories

#### B. `_get_monthly_product_data()` Method Issues
**Location**: `custom_modules/dashboard_pos/models/pos_order.py` lines 752-781

**Problems**:
- Uses `AVG(price_unit)` which can be misleading
- Limited to POS-available products only
- No detailed product information
- No return/refund handling

### 2. Data Source Analysis

#### Primary Data Source: `pos_order_line` Table
```sql
-- Key fields in pos_order_line:
- id: Primary key
- order_id: Links to pos_order
- product_id: Links to product_product
- qty: Quantity (can be negative for returns)
- price_unit: Unit price at time of sale
- price_subtotal: Total line amount
- total_cost: Cost of goods sold
- discount: Discount amount
- full_product_name: Product name at time of sale
```

#### Supporting Tables:
- `pos_order`: Order context (date, state, company)
- `product_product`: Product variants
- `product_template`: Product master data
- `product_category`: Product categories

## Solution Implementation

### 1. Create New Comprehensive Data Method

Add this method to `custom_modules/dashboard_pos/models/pos_order.py`:

```python
@api.model
def get_complete_monthly_sales_data(self, month_start, month_end):
    """
    Get complete list of all products sold in a month with prices and quantities.
    
    This method replaces the limited get_all_data() method and provides
    comprehensive monthly sales data for all products.
    
    Args:
        month_start (date): Start of month (YYYY-MM-01)
        month_end (date): End of month (YYYY-MM-01 of next month)
        
    Returns:
        dict: Complete sales data with product details
    """
    company_id = self.env.company.id
    
    # Convert dates to datetime for proper querying
    if isinstance(month_start, str):
        month_start = datetime.strptime(month_start, '%Y-%m-%d').date()
    if isinstance(month_end, str):
        month_end = datetime.strptime(month_end, '%Y-%m-%d').date()
    
    # Main comprehensive query
    query = '''
        SELECT 
            pt.id as template_id,
            pt.name as product_name,
            pp.id as product_id,
            pp.default_code as sku,
            pt.categ_id as category_id,
            pc.name as category_name,
            pc.complete_name as category_full_name,
            SUM(pol.qty) as total_quantity,
            COUNT(DISTINCT pol.order_id) as order_count,
            COUNT(DISTINCT DATE(po.date_order)) as days_sold,
            AVG(pol.price_unit) as avg_price,
            MIN(pol.price_unit) as min_price,
            MAX(pol.price_unit) as max_price,
            SUM(pol.price_subtotal) as total_revenue,
            AVG(pol.total_cost) as avg_cost,
            SUM(pol.total_cost) as total_cost,
            pp.standard_price as standard_cost,
            pt.list_price as list_price,
            pt.available_in_pos as pos_available,
            pp.qty_available as current_stock,
            pt.sale_ok as sale_ok,
            pt.purchase_ok as purchase_ok,
            -- Calculate price variance
            STDDEV(pol.price_unit) as price_stddev,
            -- Calculate return quantities
            SUM(CASE WHEN pol.qty < 0 THEN pol.qty ELSE 0 END) as return_quantity,
            SUM(CASE WHEN pol.qty > 0 THEN pol.qty ELSE 0 END) as sale_quantity
        FROM pos_order_line pol
        INNER JOIN pos_order po ON pol.order_id = po.id
        INNER JOIN product_product pp ON pol.product_id = pp.id
        INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
        LEFT JOIN product_category pc ON pt.categ_id = pc.id
        WHERE po.company_id = %s
            AND po.date_order >= %s
            AND po.date_order < %s
            AND po.state IN ('paid', 'done', 'invoiced')
        GROUP BY 
            pt.id, pt.name, pp.id, pp.default_code, 
            pt.categ_id, pc.name, pc.complete_name,
            pp.standard_price, pt.list_price, 
            pt.available_in_pos, pp.qty_available,
            pt.sale_ok, pt.purchase_ok
        HAVING SUM(pol.qty) != 0
        ORDER BY SUM(pol.price_subtotal) DESC
    '''
    
    self._cr.execute(query, (company_id, month_start, month_end))
    raw_data = self._cr.dictfetchall()
    
    # Process and enhance the data
    processed_data = []
    total_revenue = 0
    total_quantity = 0
    
    for row in raw_data:
        # Calculate margins and percentages
        margin_amount = row['total_revenue'] - row['total_cost']
        margin_percentage = (margin_amount / row['total_revenue'] * 100) if row['total_revenue'] > 0 else 0
        
        # Determine price consistency
        price_variance = row['price_stddev'] or 0
        price_consistency = 'consistent' if price_variance < 0.01 else 'variable'
        
        # Calculate turnover ratio
        turnover_ratio = (row['total_quantity'] / max(row['current_stock'], 1)) if row['current_stock'] > 0 else 0
        
        # Calculate average daily sales
        avg_daily_sales = (row['total_quantity'] / max(row['days_sold'], 1)) if row['days_sold'] > 0 else 0
        
        processed_row = {
            'template_id': row['template_id'],
            'product_id': row['product_id'],
            'product_name': row['product_name'],
            'sku': row['sku'] or '',
            'category_id': row['category_id'],
            'category_name': row['category_name'] or 'Uncategorized',
            'category_full_name': row['category_full_name'] or 'Uncategorized',
            'total_quantity': round(row['total_quantity'], 2),
            'sale_quantity': round(row['sale_quantity'], 2),
            'return_quantity': round(row['return_quantity'], 2),
            'order_count': row['order_count'],
            'days_sold': row['days_sold'],
            'avg_daily_sales': round(avg_daily_sales, 2),
            'avg_price': round(row['avg_price'], 2),
            'min_price': round(row['min_price'], 2),
            'max_price': round(row['max_price'], 2),
            'price_stddev': round(price_variance, 2),
            'price_consistency': price_consistency,
            'total_revenue': round(row['total_revenue'], 2),
            'avg_cost': round(row['avg_cost'], 2),
            'total_cost': round(row['total_cost'], 2),
            'standard_cost': round(row['standard_cost'], 2),
            'list_price': round(row['list_price'], 2),
            'margin_amount': round(margin_amount, 2),
            'margin_percentage': round(margin_percentage, 2),
            'pos_available': row['pos_available'],
            'sale_ok': row['sale_ok'],
            'purchase_ok': row['purchase_ok'],
            'current_stock': round(row['current_stock'], 2),
            'turnover_ratio': round(turnover_ratio, 2)
        }
        
        processed_data.append(processed_row)
        total_revenue += row['total_revenue']
        total_quantity += row['total_quantity']
    
    return {
        'month_start': month_start.strftime('%Y-%m-%d'),
        'month_end': month_end.strftime('%Y-%m-%d'),
        'total_products': len(processed_data),
        'total_revenue': round(total_revenue, 2),
        'total_quantity': round(total_quantity, 2),
        'products': processed_data
    }
```

### 2. Update Existing Methods

#### A. Update `get_all_data()` Method
Replace the existing method with a call to the new comprehensive method:

```python
@api.model
def get_all_data(self, from_date_cus, to_date_cus):
    """
    Updated method that uses the comprehensive data source.
    Maintains backward compatibility while providing better data.
    """
    # Get comprehensive data
    complete_data = self.get_complete_monthly_sales_data(from_date_cus, to_date_cus)
    
    # Format for backward compatibility
    top_selling_product_pos = []
    top_selling_product_inv = []
    low_selling_product_pos = []
    low_selling_product_inv = []
    
    # Sort products by revenue for top selling
    sorted_by_revenue = sorted(complete_data['products'], 
                              key=lambda x: x['total_revenue'], 
                              reverse=True)
    
    # Get top 5 POS products
    pos_products = [p for p in sorted_by_revenue if p['pos_available']]
    for i, product in enumerate(pos_products[:5]):
        top_selling_product_pos.append({
            'id': product['template_id'],
            'product': product['product_id'],
            'product_name': {'en_US': product['product_name']},
            'total_quantity': product['total_quantity'],
            'price': product['avg_price'],
            'available_quantity': product['current_stock'],
            'cost': product['avg_cost']
        })
    
    # Get top 5 inventory products (all products)
    for i, product in enumerate(sorted_by_revenue[:5]):
        top_selling_product_inv.append({
            'id': product['template_id'],
            'product': product['product_id'],
            'product_name': {'en_US': product['product_name']},
            'total_quantity': product['total_quantity'],
            'price': product['avg_price'],
            'available_quantity': product['current_stock'],
            'cost': product['avg_cost']
        })
    
    # Get low selling products (bottom 5)
    low_selling = sorted_by_revenue[-5:] if len(sorted_by_revenue) >= 5 else sorted_by_revenue
    for product in low_selling:
        if product['pos_available']:
            low_selling_product_pos.append({
                'id': product['template_id'],
                'product': product['product_id'],
                'product_name': {'en_US': product['product_name']},
                'total_quantity': product['total_quantity'],
                'price': product['avg_price'],
                'available_quantity': product['current_stock'],
                'cost': product['avg_cost']
            })
        
        low_selling_product_inv.append({
            'id': product['template_id'],
            'product': product['product_id'],
            'product_name': {'en_US': product['product_name']},
            'total_quantity': product['total_quantity'],
            'price': product['avg_price'],
            'available_quantity': product['current_stock'],
            'cost': product['avg_cost']
        })
    
    # Get payment details (keep existing logic)
    query = """
        SELECT pos_payment_method.name, SUM(amount) 
        FROM pos_payment 
        INNER JOIN pos_payment_method ON pos_payment_method.id = pos_payment.payment_method_id 
        WHERE DATE(pos_payment.payment_date) >= %s 
        AND DATE(pos_payment.payment_date) <= %s 
        GROUP BY pos_payment_method.name 
        ORDER BY SUM(amount) DESC;
    """
    self._cr.execute(query, (from_date_cus, to_date_cus,))
    payment_details = self._cr.fetchall()
    
    return {
        'top_selling_product_pos': top_selling_product_pos,
        'top_selling_product_inv': top_selling_product_inv,
        'low_selling_product_pos': low_selling_product_pos,
        'low_selling_product_inv': low_selling_product_inv,
        'payment_details': payment_details,
        'complete_data': complete_data  # Add complete data for new features
    }
```

#### B. Update `_get_monthly_product_data()` Method
Replace the existing method to use the comprehensive data:

```python
def _get_monthly_product_data(self, month_start, month_end):
    """
    Updated method that uses comprehensive data for pricing scenarios.
    """
    complete_data = self.get_complete_monthly_sales_data(month_start, month_end)
    
    # Convert to pricing scenarios format
    pricing_data = []
    for product in complete_data['products']:
        pricing_data.append({
            'product_name': product['product_name'],
            'qty': product['total_quantity'],
            'price': product['avg_price'],
            'cost': product['avg_cost']
        })
    
    # Apply VAT conversion if needed
    return self._convert_to_net_prices(pricing_data)
```

### 3. Add New Analysis Methods

#### A. Product Performance Analysis
```python
@api.model
def get_product_performance_analysis(self, month_start, month_end):
    """
    Get detailed product performance analysis.
    """
    complete_data = self.get_complete_monthly_sales_data(month_start, month_end)
    
    # Calculate performance metrics
    total_products = len(complete_data['products'])
    total_revenue = complete_data['total_revenue']
    
    # Categorize products by performance
    high_performers = []
    medium_performers = []
    low_performers = []
    
    for product in complete_data['products']:
        revenue_share = (product['total_revenue'] / total_revenue * 100) if total_revenue > 0 else 0
        
        if revenue_share >= 5:  # Top 5% revenue share
            high_performers.append(product)
        elif revenue_share >= 1:  # 1-5% revenue share
            medium_performers.append(product)
        else:  # <1% revenue share
            low_performers.append(product)
    
    return {
        'summary': {
            'total_products': total_products,
            'total_revenue': total_revenue,
            'high_performers_count': len(high_performers),
            'medium_performers_count': len(medium_performers),
            'low_performers_count': len(low_performers)
        },
        'high_performers': high_performers,
        'medium_performers': medium_performers,
        'low_performers': low_performers
    }
```

#### B. Category Analysis
```python
@api.model
def get_category_analysis(self, month_start, month_end):
    """
    Get sales analysis by product category.
    """
    complete_data = self.get_complete_monthly_sales_data(month_start, month_end)
    
    # Group by category
    category_data = {}
    for product in complete_data['products']:
        category_name = product['category_name']
        
        if category_name not in category_data:
            category_data[category_name] = {
                'category_name': category_name,
                'product_count': 0,
                'total_quantity': 0,
                'total_revenue': 0,
                'total_cost': 0,
                'margin_amount': 0,
                'products': []
            }
        
        category_data[category_name]['product_count'] += 1
        category_data[category_name]['total_quantity'] += product['total_quantity']
        category_data[category_name]['total_revenue'] += product['total_revenue']
        category_data[category_name]['total_cost'] += product['total_cost']
        category_data[category_name]['margin_amount'] += product['margin_amount']
        category_data[category_name]['products'].append(product)
    
    # Calculate percentages and sort
    for category in category_data.values():
        category['revenue_share'] = (category['total_revenue'] / complete_data['total_revenue'] * 100) if complete_data['total_revenue'] > 0 else 0
        category['margin_percentage'] = (category['margin_amount'] / category['total_revenue'] * 100) if category['total_revenue'] > 0 else 0
    
    # Sort by revenue
    sorted_categories = sorted(category_data.values(), 
                              key=lambda x: x['total_revenue'], 
                              reverse=True)
    
    return sorted_categories
```

### 4. Add Export Functionality

```python
@api.model
def export_monthly_sales_data(self, month_start, month_end, format='csv'):
    """
    Export monthly sales data in various formats.
    
    Args:
        month_start (date): Start of month
        month_end (date): End of month
        format (str): Export format ('csv', 'excel', 'json')
    """
    complete_data = self.get_complete_monthly_sales_data(month_start, month_end)
    
    if format == 'csv':
        return self._export_to_csv(complete_data)
    elif format == 'excel':
        return self._export_to_excel(complete_data)
    elif format == 'json':
        return json.dumps(complete_data, indent=2, default=str)
    else:
        raise ValueError(f"Unsupported format: {format}")

def _export_to_csv(self, data):
    """Export data to CSV format."""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    headers = [
        'Product Name', 'SKU', 'Category', 'Total Quantity', 'Sale Quantity', 'Return Quantity',
        'Order Count', 'Days Sold', 'Avg Daily Sales', 'Avg Price', 'Min Price', 'Max Price',
        'Price StdDev', 'Price Consistency', 'Total Revenue', 'Avg Cost', 'Total Cost',
        'Standard Cost', 'List Price', 'Margin Amount', 'Margin %', 'Current Stock',
        'Turnover Ratio', 'POS Available', 'Sale OK', 'Purchase OK'
    ]
    writer.writerow(headers)
    
    # Write data
    for product in data['products']:
        writer.writerow([
            product['product_name'],
            product['sku'],
            product['category_name'],
            product['total_quantity'],
            product['sale_quantity'],
            product['return_quantity'],
            product['order_count'],
            product['days_sold'],
            product['avg_daily_sales'],
            product['avg_price'],
            product['min_price'],
            product['max_price'],
            product['price_stddev'],
            product['price_consistency'],
            product['total_revenue'],
            product['avg_cost'],
            product['total_cost'],
            product['standard_cost'],
            product['list_price'],
            product['margin_amount'],
            product['margin_percentage'],
            product['current_stock'],
            product['turnover_ratio'],
            product['pos_available'],
            product['sale_ok'],
            product['purchase_ok']
        ])
    
    return output.getvalue()
```

## Testing and Validation

### 1. Unit Tests
Create test file: `custom_modules/dashboard_pos/tests/test_monthly_sales_data.py`

```python
import unittest
from datetime import date, timedelta
from odoo.tests.common import TransactionCase

class TestMonthlySalesData(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.pos_order_model = self.env['pos.order']
        
    def test_get_complete_monthly_sales_data(self):
        """Test the comprehensive monthly sales data method."""
        # Create test data
        month_start = date.today().replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        
        # Call the method
        result = self.pos_order_model.get_complete_monthly_sales_data(month_start, month_end)
        
        # Validate structure
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
        
    def test_data_accuracy(self):
        """Test data accuracy and calculations."""
        month_start = date.today().replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        
        result = self.pos_order_model.get_complete_monthly_sales_data(month_start, month_end)
        
        # Validate calculations
        calculated_total_revenue = sum(p['total_revenue'] for p in result['products'])
        calculated_total_quantity = sum(p['total_quantity'] for p in result['products'])
        
        self.assertAlmostEqual(result['total_revenue'], calculated_total_revenue, places=2)
        self.assertAlmostEqual(result['total_quantity'], calculated_total_quantity, places=2)
        
        # Validate margin calculations
        for product in result['products']:
            expected_margin = product['total_revenue'] - product['total_cost']
            self.assertAlmostEqual(product['margin_amount'], expected_margin, places=2)
```

### 2. Integration Tests
Test the integration with existing dashboard functionality:

```python
def test_dashboard_integration(self):
    """Test integration with existing dashboard methods."""
    from_date = date.today().replace(day=1)
    to_date = (from_date + timedelta(days=32)).replace(day=1)
    
    # Test updated get_all_data method
    result = self.pos_order_model.get_all_data(from_date, to_date)
    
    # Validate backward compatibility
    self.assertIn('top_selling_product_pos', result)
    self.assertIn('top_selling_product_inv', result)
    self.assertIn('low_selling_product_pos', result)
    self.assertIn('low_selling_product_inv', result)
    self.assertIn('payment_details', result)
    self.assertIn('complete_data', result)
    
    # Validate data structure
    self.assertIsInstance(result['top_selling_product_pos'], list)
    self.assertIsInstance(result['complete_data'], dict)
```

## Performance Optimization

### 1. Database Indexes
Add these indexes to improve query performance:

```sql
-- Index on pos_order for date and company filtering
CREATE INDEX idx_pos_order_date_company ON pos_order (date_order, company_id, state);

-- Index on pos_order_line for product and order filtering
CREATE INDEX idx_pos_order_line_product_order ON pos_order_line (product_id, order_id);

-- Index on product_template for POS availability
CREATE INDEX idx_product_template_pos ON product_template (available_in_pos, id);

-- Composite index for the main query
CREATE INDEX idx_pos_order_line_comprehensive ON pos_order_line (order_id, product_id, qty, price_unit);
```

### 2. Caching Strategy
Implement caching for frequently accessed data:

```python
from odoo import api, fields, models
import hashlib
import json

class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    @api.model
    def get_complete_monthly_sales_data_cached(self, month_start, month_end):
        """
        Cached version of the comprehensive data method.
        """
        # Create cache key
        cache_key = f"monthly_sales_{month_start}_{month_end}_{self.env.company.id}"
        
        # Check cache first
        cached_data = self.env.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # Get fresh data
        data = self.get_complete_monthly_sales_data(month_start, month_end)
        
        # Cache for 1 hour
        self.env.cache.set(cache_key, data, ttl=3600)
        
        return data
```

## Migration Strategy

### 1. Backward Compatibility
- Keep existing method signatures
- Add new methods alongside old ones
- Gradually migrate dashboard components
- Maintain API compatibility

### 2. Gradual Rollout
1. **Phase 1**: Add new methods without changing existing ones
2. **Phase 2**: Update dashboard to use new methods
3. **Phase 3**: Add new analysis features
4. **Phase 4**: Remove deprecated methods

### 3. Data Validation
- Compare results between old and new methods
- Validate data accuracy with sample datasets
- Test performance with large datasets
- Monitor for any data discrepancies

## Conclusion

This implementation provides a comprehensive solution for retrieving complete monthly product sales data. The new approach:

1. **Solves Current Issues**: Provides complete data instead of limited top 5/10
2. **Improves Data Quality**: Better aggregation and price handling
3. **Enhances Functionality**: Adds detailed analysis capabilities
4. **Maintains Compatibility**: Works with existing dashboard features
5. **Enables Future Features**: Foundation for advanced analytics

The implementation is designed to be backward compatible while providing a solid foundation for your ultimate target of having complete visibility into monthly product sales performance.
