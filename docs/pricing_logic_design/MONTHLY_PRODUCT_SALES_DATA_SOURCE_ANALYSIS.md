# Monthly Product Sales Data Source Analysis

## Overview
This document analyzes where to find the complete list of all products sold in one month with their prices and quantities, which is the foundation for pricing scenarios calculations and other business intelligence features.

## Current Implementation Analysis

### 1. Data Sources in the System

#### A. POS Order Lines (Primary Source)
**Location**: `pos_order_line` table
**Key Fields**:
- `product_id` - Links to `product_product`
- `qty` - Quantity sold (can be negative for returns)
- `price_unit` - Unit price at time of sale
- `price_subtotal` - Total line amount
- `total_cost` - Cost of goods sold
- `order_id` - Links to `pos_order`

**Current Query Pattern** (from `pos_order.py` lines 90-103):
```sql
SELECT 
    (product_template.name) AS product_name,
    product_template.id as id,
    product_product.id as product,
    SUM(qty) AS total_quantity,
    pos_order_line.price_unit AS price 
FROM pos_order_line 
INNER JOIN product_product ON product_product.id = pos_order_line.product_id 
INNER JOIN product_template ON product_product.product_tmpl_id = product_template.id 
INNER JOIN pos_order ON pos_order_line.order_id = pos_order.id
WHERE pos_order_line.company_id = %s 
  AND DATE(pos_order.date_order) >= %s 
  AND DATE(pos_order.date_order) <= %s 
  AND product_template.available_in_pos = True 
GROUP BY product_template.name, pos_order_line.price_unit, product_template.id, product_product.id
ORDER BY total_quantity DESC 
LIMIT 5
```

#### B. Product Information
**Location**: `product_template` and `product_product` tables
**Key Fields**:
- `name` - Product name
- `standard_price` - Standard cost
- `list_price` - List price
- `available_in_pos` - POS availability flag
- `qty_available` - Current stock quantity

#### C. Order Context
**Location**: `pos_order` table
**Key Fields**:
- `date_order` - Order timestamp
- `state` - Order status ('paid', 'done', 'invoiced')
- `amount_total` - Total order amount
- `company_id` - Company filter

### 2. Current Data Retrieval Methods

#### A. Top Selling Products (POS) - `get_all_data()` method
```python
# Lines 90-103 in pos_order.py
query = '''SELECT (product_template.name) AS product_name,product_template.id as id,product_product.id as product,
                  SUM(qty) AS total_quantity,
                  pos_order_line.price_unit AS price 
           FROM pos_order_line 
           INNER JOIN product_product ON product_product.id = pos_order_line.product_id 
           INNER JOIN product_template ON product_product.product_tmpl_id = product_template.id 
           INNER JOIN pos_order ON pos_order_line.order_id = pos_order.id
           WHERE pos_order_line.company_id = %s 
             AND DATE(pos_order.date_order) >= %s 
             AND DATE(pos_order.date_order) <= %s 
             AND product_template.available_in_pos = True 
           GROUP BY product_template.name, pos_order_line.price_unit, product_template.id,product_product.id
           ORDER BY total_quantity DESC 
           LIMIT 5'''
```

#### B. Pricing Scenarios Data - `_get_monthly_product_data()` method
```python
# Lines 757-775 in pos_order.py
query = '''
    SELECT 
        product_template.name AS product_name,
        SUM(pos_order_line.qty) AS qty,
        AVG(pos_order_line.price_unit) AS price,
        product_product.standard_price AS cost
    FROM pos_order_line 
    INNER JOIN product_product ON product_product.id = pos_order_line.product_id 
    INNER JOIN product_template ON product_product.product_tmpl_id = product_template.id 
    INNER JOIN pos_order ON pos_order_line.order_id = pos_order.id
    WHERE pos_order_line.company_id = %s 
        AND pos_order.date_order >= %s 
        AND pos_order.date_order < %s 
        AND pos_order.state IN ('paid', 'done', 'invoiced')
        AND product_template.available_in_pos = True
    GROUP BY product_template.name, product_product.standard_price
    HAVING SUM(pos_order_line.qty) != 0
    ORDER BY product_template.name
'''
```

### 3. Issues with Current Implementation

#### A. Data Aggregation Problems
1. **Price Averaging Issue**: Using `AVG(pos_order_line.price_unit)` can be misleading if prices changed during the month
2. **Grouping by Price**: Current queries group by `price_unit`, creating separate rows for same product at different prices
3. **Limited Scope**: Most queries use `LIMIT 5` or `LIMIT 10`, not getting complete monthly data

#### B. Missing Data Points
1. **No Return Handling**: Returns are included as negative quantities but not properly categorized
2. **No Discount Analysis**: No breakdown of discounts vs. regular prices
3. **No Time-based Analysis**: No hourly/daily breakdown within the month

#### C. Performance Issues
1. **Multiple Queries**: Separate queries for POS vs Inventory products
2. **No Caching**: Data is recalculated on every request
3. **Inefficient Grouping**: Complex GROUP BY clauses

## Recommended Solution

### 1. Create a Comprehensive Monthly Sales Data Method

```python
@api.model
def get_complete_monthly_sales_data(self, month_start, month_end):
    """
    Get complete list of all products sold in a month with prices and quantities.
    
    Args:
        month_start (date): Start of month
        month_end (date): End of month
        
    Returns:
        dict: Complete sales data with product details
    """
    company_id = self.env.company.id
    
    # Main query for all products sold in the month
    query = '''
        SELECT 
            pt.id as template_id,
            pt.name as product_name,
            pp.id as product_id,
            pp.default_code as sku,
            pt.categ_id as category_id,
            pc.name as category_name,
            SUM(pol.qty) as total_quantity,
            COUNT(DISTINCT pol.order_id) as order_count,
            AVG(pol.price_unit) as avg_price,
            MIN(pol.price_unit) as min_price,
            MAX(pol.price_unit) as max_price,
            SUM(pol.price_subtotal) as total_revenue,
            AVG(pol.total_cost) as avg_cost,
            SUM(pol.total_cost) as total_cost,
            pp.standard_price as standard_cost,
            pt.list_price as list_price,
            pt.available_in_pos as pos_available,
            pp.qty_available as current_stock
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
            pt.categ_id, pc.name, pp.standard_price, 
            pt.list_price, pt.available_in_pos, pp.qty_available
        HAVING SUM(pol.qty) != 0
        ORDER BY SUM(pol.price_subtotal) DESC
    '''
    
    self._cr.execute(query, (company_id, month_start, month_end))
    raw_data = self._cr.dictfetchall()
    
    # Process and enhance the data
    processed_data = []
    for row in raw_data:
        # Calculate margins and percentages
        margin_amount = row['total_revenue'] - row['total_cost']
        margin_percentage = (margin_amount / row['total_revenue'] * 100) if row['total_revenue'] > 0 else 0
        
        # Determine price consistency
        price_consistency = 'consistent' if row['min_price'] == row['max_price'] else 'variable'
        
        processed_data.append({
            'template_id': row['template_id'],
            'product_id': row['product_id'],
            'product_name': row['product_name'],
            'sku': row['sku'] or '',
            'category_id': row['category_id'],
            'category_name': row['category_name'] or 'Uncategorized',
            'total_quantity': round(row['total_quantity'], 2),
            'order_count': row['order_count'],
            'avg_price': round(row['avg_price'], 2),
            'min_price': round(row['min_price'], 2),
            'max_price': round(row['max_price'], 2),
            'price_consistency': price_consistency,
            'total_revenue': round(row['total_revenue'], 2),
            'avg_cost': round(row['avg_cost'], 2),
            'total_cost': round(row['total_cost'], 2),
            'standard_cost': round(row['standard_cost'], 2),
            'list_price': round(row['list_price'], 2),
            'margin_amount': round(margin_amount, 2),
            'margin_percentage': round(margin_percentage, 2),
            'pos_available': row['pos_available'],
            'current_stock': round(row['current_stock'], 2),
            'turnover_ratio': round(row['total_quantity'] / max(row['current_stock'], 1), 2)
        })
    
    return {
        'month_start': month_start,
        'month_end': month_end,
        'total_products': len(processed_data),
        'total_revenue': sum(item['total_revenue'] for item in processed_data),
        'total_quantity': sum(item['total_quantity'] for item in processed_data),
        'products': processed_data
    }
```

### 2. Enhanced Data Retrieval for Specific Use Cases

#### A. For Pricing Scenarios
```python
@api.model
def get_pricing_scenarios_data(self, month_start, month_end):
    """
    Get data specifically formatted for pricing scenarios calculations.
    """
    complete_data = self.get_complete_monthly_sales_data(month_start, month_end)
    
    # Filter and format for pricing scenarios
    pricing_data = []
    for product in complete_data['products']:
        # Use average price for consistency
        pricing_data.append({
            'product_name': product['product_name'],
            'qty': product['total_quantity'],
            'price': product['avg_price'],
            'cost': product['avg_cost']
        })
    
    return pricing_data
```

#### B. For Top Selling Analysis
```python
@api.model
def get_top_selling_analysis(self, month_start, month_end, limit=20, sort_by='revenue'):
    """
    Get top selling products with detailed analysis.
    
    Args:
        sort_by: 'revenue', 'quantity', 'margin', 'orders'
    """
    complete_data = self.get_complete_monthly_sales_data(month_start, month_end)
    
    # Sort by specified criteria
    sort_keys = {
        'revenue': lambda x: x['total_revenue'],
        'quantity': lambda x: x['total_quantity'],
        'margin': lambda x: x['margin_amount'],
        'orders': lambda x: x['order_count']
    }
    
    sorted_products = sorted(
        complete_data['products'], 
        key=sort_keys.get(sort_by, sort_keys['revenue']), 
        reverse=True
    )
    
    return sorted_products[:limit]
```

### 3. Data Export and Reporting

#### A. CSV Export Method
```python
@api.model
def export_monthly_sales_csv(self, month_start, month_end):
    """
    Export monthly sales data to CSV format.
    """
    import csv
    import io
    
    data = self.get_complete_monthly_sales_data(month_start, month_end)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    headers = [
        'Product Name', 'SKU', 'Category', 'Total Quantity', 'Order Count',
        'Avg Price', 'Min Price', 'Max Price', 'Price Consistency',
        'Total Revenue', 'Avg Cost', 'Total Cost', 'Standard Cost',
        'List Price', 'Margin Amount', 'Margin %', 'Current Stock', 'Turnover Ratio'
    ]
    writer.writerow(headers)
    
    # Write data
    for product in data['products']:
        writer.writerow([
            product['product_name'],
            product['sku'],
            product['category_name'],
            product['total_quantity'],
            product['order_count'],
            product['avg_price'],
            product['min_price'],
            product['max_price'],
            product['price_consistency'],
            product['total_revenue'],
            product['avg_cost'],
            product['total_cost'],
            product['standard_cost'],
            product['list_price'],
            product['margin_amount'],
            product['margin_percentage'],
            product['current_stock'],
            product['turnover_ratio']
        ])
    
    return output.getvalue()
```

## Implementation Plan

### Phase 1: Core Data Method
1. Implement `get_complete_monthly_sales_data()` method
2. Add comprehensive error handling and validation
3. Add unit tests for data accuracy

### Phase 2: Enhanced Analysis Methods
1. Implement specialized methods for different use cases
2. Add caching mechanism for performance
3. Add data validation and consistency checks

### Phase 3: Export and Reporting
1. Add CSV export functionality
2. Add Excel export with formatting
3. Add scheduled reports

### Phase 4: Integration
1. Update existing dashboard methods to use new data source
2. Update pricing scenarios to use comprehensive data
3. Add new dashboard widgets for detailed analysis

## Data Quality Considerations

### 1. Data Validation
- Ensure all required fields are present
- Validate date ranges
- Check for data consistency
- Handle edge cases (zero quantities, missing costs)

### 2. Performance Optimization
- Add database indexes on frequently queried fields
- Implement query result caching
- Use pagination for large datasets
- Consider materialized views for complex aggregations

### 3. Data Accuracy
- Handle returns and refunds properly
- Account for price changes during the month
- Validate cost calculations
- Ensure proper currency handling

## Conclusion

The current implementation has several limitations in retrieving complete monthly product sales data. The recommended solution provides a comprehensive method to get all products sold in a month with their prices and quantities, which can serve as the foundation for pricing scenarios, business intelligence, and other analytical features.

The new approach addresses the current issues by:
1. Providing complete data (not just top 5/10)
2. Using proper aggregation methods
3. Including comprehensive product information
4. Supporting multiple use cases
5. Enabling data export and reporting

This foundation will support your ultimate target of having complete visibility into monthly product sales performance and enable more sophisticated pricing and business intelligence features.
