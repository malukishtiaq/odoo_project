# -*- coding: utf-8 -*-
"""
Post-migration script to add database indexes for performance optimization
"""

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Add database indexes for better performance"""
    
    # Indexes for pos_order_line table
    indexes_to_create = [
        # Composite index for date range queries
        "CREATE INDEX IF NOT EXISTS idx_pos_order_line_date_company ON pos_order_line (order_id, product_id) INCLUDE (qty, price_unit, price_subtotal, total_cost)",
        
        # Index for product queries
        "CREATE INDEX IF NOT EXISTS idx_pos_order_line_product ON pos_order_line (product_id) INCLUDE (qty, price_unit, price_subtotal)",
        
        # Index for order date queries
        "CREATE INDEX IF NOT EXISTS idx_pos_order_date_company ON pos_order (date_order, company_id, state) INCLUDE (amount_total)",
        
        # Index for product template queries
        "CREATE INDEX IF NOT EXISTS idx_product_template_pos ON product_template (available_in_pos, sale_ok) INCLUDE (name, list_price)",
        
        # Index for product category queries
        "CREATE INDEX IF NOT EXISTS idx_product_category_name ON product_category (name) INCLUDE (complete_name)",
    ]
    
    for index_sql in indexes_to_create:
        try:
            cr.execute(index_sql)
            _logger.info(f"Successfully created index: {index_sql}")
        except Exception as e:
            _logger.warning(f"Could not create index: {index_sql}. Error: {str(e)}")
    
    _logger.info("Database indexes optimization completed")
