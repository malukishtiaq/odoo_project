# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class PricingScenariosController(http.Controller):

    @http.route('/api/pricing-scenarios', type='http', auth='user', methods=['GET'], csrf=False)
    def get_pricing_scenarios(self, month=None, **kwargs):
        """
        API endpoint to get pricing scenarios for a given month.
        
        Args:
            month (str): Month in YYYY-MM format (e.g., '2024-01')
        
        Returns:
            JSON response with pricing scenarios data
        """
        try:
            if not month:
                return request.make_json_response({
                    'status': 'error',
                    'message': 'Month parameter is required (YYYY-MM format)'
                }, status=400)
            
            # Validate month format
            try:
                year, month_num = map(int, month.split('-'))
                if not (1 <= month_num <= 12):
                    raise ValueError("Invalid month number")
            except (ValueError, IndexError):
                return request.make_json_response({
                    'status': 'error',
                    'message': 'Invalid month format. Use YYYY-MM format (e.g., 2024-01)'
                }, status=400)
            
            # Check if month is in the past
            from datetime import datetime, date
            current_date = date.today()
            requested_date = date(year, month_num, 1)
            
            if requested_date >= current_date.replace(day=1):
                return request.make_json_response({
                    'status': 'error',
                    'message': 'Only previous months are allowed for pricing scenarios'
                }, status=400)
            
            # Get pricing scenarios from the model
            pos_order_model = request.env['pos.order']
            result = pos_order_model.get_pricing_scenarios(month)
            
            # Return appropriate status code based on result
            if result['status'] == 'insufficient':
                return request.make_json_response(result, status=422)
            elif result['status'] == 'error':
                return request.make_json_response(result, status=500)
            else:
                return request.make_json_response(result, status=200)
                
        except Exception as e:
            _logger.error(f"Error in pricing scenarios API: {str(e)}")
            return request.make_json_response({
                'status': 'error',
                'message': f'Internal server error: {str(e)}'
            }, status=500)

    @http.route('/api/pricing-scenarios/custom', type='http', auth='user', methods=['POST'], csrf=False)
    def calculate_custom_scenario(self, **kwargs):
        """
        API endpoint to calculate custom net target scenario.
        
        Expected JSON payload:
        {
            "month": "2024-01",
            "target": 25000
        }
        
        Returns:
            JSON response with custom pricing scenario data
        """
        try:
            # Get JSON data from request
            data = json.loads(request.httprequest.data.decode('utf-8'))
            
            month = data.get('month')
            target = data.get('target')
            
            if not month:
                return request.make_json_response({
                    'status': 'error',
                    'message': 'Month parameter is required'
                }, status=400)
            
            if not target:
                return request.make_json_response({
                    'status': 'error',
                    'message': 'Target parameter is required'
                }, status=400)
            
            try:
                target = float(target)
                if target <= 0:
                    raise ValueError("Target must be positive")
            except (ValueError, TypeError):
                return request.make_json_response({
                    'status': 'error',
                    'message': 'Target must be a positive number'
                }, status=400)
            
            # Validate month format
            try:
                year, month_num = map(int, month.split('-'))
                if not (1 <= month_num <= 12):
                    raise ValueError("Invalid month number")
            except (ValueError, IndexError):
                return request.make_json_response({
                    'status': 'error',
                    'message': 'Invalid month format. Use YYYY-MM format (e.g., 2024-01)'
                }, status=400)
            
            # Check if month is in the past
            from datetime import datetime, date
            current_date = date.today()
            requested_date = date(year, month_num, 1)
            
            if requested_date >= current_date.replace(day=1):
                return request.make_json_response({
                    'status': 'error',
                    'message': 'Only previous months are allowed for pricing scenarios'
                }, status=400)
            
            # Calculate custom scenario
            pos_order_model = request.env['pos.order']
            result = pos_order_model.calculate_custom_net_scenario(month, target)
            
            # Return appropriate status code based on result
            if result['status'] == 'insufficient':
                return request.make_json_response(result, status=422)
            elif result['status'] == 'error':
                return request.make_json_response(result, status=500)
            else:
                return request.make_json_response(result, status=200)
                
        except json.JSONDecodeError:
            return request.make_json_response({
                'status': 'error',
                'message': 'Invalid JSON payload'
            }, status=400)
        except Exception as e:
            _logger.error(f"Error in custom pricing scenario API: {str(e)}")
            return request.make_json_response({
                'status': 'error',
                'message': f'Internal server error: {str(e)}'
            }, status=500)

    @http.route('/api/pricing-scenarios/date-range', type='http', auth='user', methods=['GET'], csrf=False)
    def get_pricing_scenarios_date_range(self, start_date=None, end_date=None, **kwargs):
        """
        API endpoint to get pricing scenarios for a specific date range.
        Similar to the existing date range filter in the dashboard.
        
        Parameters:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            JSON response with pricing scenarios data for the date range
        """
        try:
            from datetime import datetime, date
            import logging
            
            _logger = logging.getLogger(__name__)
            
            # Validate date parameters
            if not start_date or not end_date:
                return request.make_json_response({
                    'status': 'error',
                    'message': 'Both start_date and end_date parameters are required'
                }, status=400)
            
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return request.make_json_response({
                    'status': 'error',
                    'message': 'Invalid date format. Use YYYY-MM-DD format'
                }, status=400)
            
            # Validate date range
            if start_dt > end_dt:
                return request.make_json_response({
                    'status': 'error',
                    'message': 'Start date cannot be after end date'
                }, status=400)
            
            # Get pricing scenarios for the date range
            pos_order = request.env['pos.order']
            
            # Check if the method exists (it was removed from the model)
            if not hasattr(pos_order, 'get_pricing_scenarios_date_range'):
                return request.make_json_response({
                    'status': 'error',
                    'message': 'Date range pricing scenarios feature is not available. Please use the month-based pricing scenarios instead.',
                    'suggestion': 'Try using the original month-based pricing scenarios feature.'
                }, status=501)
            
            scenarios = pos_order.get_pricing_scenarios_date_range(start_dt, end_dt)
            
            return request.make_json_response({
                'status': 'success',
                'data': scenarios,
                'date_range': {
                    'start_date': start_date,
                    'end_date': end_date
                }
            }, status=200)
            
        except Exception as e:
            _logger.error(f"Error getting pricing scenarios for date range {start_date} to {end_date}: {str(e)}")
            return request.make_json_response({
                'status': 'error',
                'message': f'Internal server error: {str(e)}'
            }, status=500)

    @http.route('/api/pricing-scenarios/months', type='http', auth='user', methods=['GET'], csrf=False)
    def get_available_months(self, **kwargs):
        """
        API endpoint to get list of available months for pricing scenarios.
        Returns months with sales data in descending order.
        
        Returns:
            JSON response with list of available months in format:
            {
                "months": [
                    { "value": "2025-09", "label": "September 2025" },
                    { "value": "2025-08", "label": "August 2025" }
                ]
            }
        """
        try:
            from datetime import datetime, date
            from dateutil.relativedelta import relativedelta
            
            # Execute SQL query to get distinct months with sales data
            query = """
                SELECT DISTINCT 
                    TO_CHAR(DATE_TRUNC('month', date_order), 'YYYY-MM') AS value,
                    TO_CHAR(DATE_TRUNC('month', date_order), 'Month YYYY') AS label
                FROM pos_order 
                WHERE date_order < DATE_TRUNC('month', CURRENT_DATE)
                    AND state IN ('paid', 'done', 'invoiced')
                    AND company_id = %s
                ORDER BY value DESC
            """
            
            # Execute the query
            request.env.cr.execute(query, (request.env.company.id,))
            results = request.env.cr.fetchall()
            
            # Format results as requested
            months = []
            for row in results:
                months.append({
                    'value': row[0],
                    'label': row[1].strip()  # Remove extra spaces from Month YYYY format
                })
            
            return request.make_json_response({
                'months': months
            }, status=200)
            
        except Exception as e:
            _logger.error(f"Error getting available months: {str(e)}")
            return request.make_json_response({
                'status': 'error',
                'message': f'Internal server error: {str(e)}'
            }, status=500)

    @http.route('/api/pricing-scenarios/available-months', type='http', auth='user', methods=['GET'], csrf=False)
    def get_available_months_legacy(self, **kwargs):
        """
        Legacy API endpoint to get list of available months for pricing scenarios.
        Returns months with sales data in descending order.
        
        Returns:
            JSON response with list of available months
        """
        try:
            from datetime import datetime, date
            from dateutil.relativedelta import relativedelta
            
            pos_order_model = request.env['pos.order']
            available_months = []
            
            # Check last 12 months for available data
            current_date = date.today()
            for i in range(1, 13):  # Skip current month, check last 12 months
                check_date = current_date.replace(day=1) - relativedelta(months=i)
                month_str = check_date.strftime('%Y-%m')
                
                # Quick check if there's any sales data for this month
                month_start = check_date
                if check_date.month == 12:
                    month_end = date(check_date.year + 1, 1, 1)
                else:
                    month_end = date(check_date.year, check_date.month + 1, 1)
                
                # Check if there are any POS orders in this month
                orders_count = request.env['pos.order'].search_count([
                    ('date_order', '>=', month_start),
                    ('date_order', '<', month_end),
                    ('state', 'in', ['paid', 'done', 'invoiced']),
                    ('company_id', '=', request.env.company.id)
                ])
                
                if orders_count > 0:
                    available_months.append({
                        'month': month_str,
                        'display': check_date.strftime('%B %Y'),
                        'orders_count': orders_count
                    })
            
            return request.make_json_response({
                'status': 'ok',
                'available_months': available_months
            }, status=200)
            
        except Exception as e:
            _logger.error(f"Error getting available months: {str(e)}")
            return request.make_json_response({
                'status': 'error',
                'message': f'Internal server error: {str(e)}'
            }, status=500)

    @http.route('/api/pricing-scenarios/apply', type='json', auth='user', methods=['POST'], csrf=False)
    def apply_pricing_scenarios(self, **kwargs):
        """
        API endpoint to apply pricing scenarios and create price lists.
        
        Expected JSON payload:
        {
            "month": "YYYY-MM",
            "scenario": "break_even|net_10k|net_custom",
            "mode": "uniform|weighted",
            "target": 10000,  // required for net_custom
            "dry_run": true,  // true=preview only; false=create price list
            "idempotency_key": "uuid"
        }
        """
        try:
            data = request.jsonrequest
            
            # Validate required fields
            required_fields = ['month', 'scenario', 'mode']
            for field in required_fields:
                if field not in data:
                    return {
                        'status': 'error',
                        'message': f'Missing required field: {field}'
                    }
            
            # Validate scenario
            if data['scenario'] not in ['break_even', 'net_10k', 'net_custom']:
                return {
                    'status': 'error',
                    'message': 'Invalid scenario. Must be break_even, net_10k, or net_custom'
                }
            
            # Validate mode
            if data['mode'] not in ['uniform', 'weighted']:
                return {
                    'status': 'error',
                    'message': 'Invalid mode. Must be uniform or weighted'
                }
            
            # Validate month format
            try:
                year, month_num = map(int, data['month'].split('-'))
                if not (1 <= month_num <= 12):
                    raise ValueError("Invalid month number")
            except (ValueError, IndexError):
                return {
                    'status': 'error',
                    'message': 'Invalid month format. Use YYYY-MM format (e.g., 2024-01)'
                }
            
            # Check if month is in the past
            from datetime import datetime, date
            current_date = date.today()
            requested_date = date(year, month_num, 1)
            
            if requested_date >= current_date.replace(day=1):
                return {
                    'status': 'error',
                    'message': 'Only previous months are allowed for pricing scenarios'
                }
            
            # Validate target for custom scenarios
            if data['scenario'] == 'net_custom':
                if 'target' not in data or not data['target']:
                    return {
                        'status': 'error',
                        'message': 'Target amount is required for custom scenarios'
                    }
                if data['target'] <= 0:
                    return {
                        'status': 'error',
                        'message': 'Target amount must be positive'
                    }
            
            # Call the model method
            pos_order_model = request.env['pos.order']
            result = pos_order_model.apply_pricing_scenarios(
                month=data['month'],
                scenario=data['scenario'],
                mode=data['mode'],
                target=data.get('target'),
                dry_run=data.get('dry_run', True),
                idempotency_key=data.get('idempotency_key')
            )
            
            return result
            
        except Exception as e:
            _logger.error(f"Error in apply_pricing_scenarios: {e}")
            return {
                'status': 'error',
                'message': f'Internal server error: {str(e)}'
            }

    @http.route('/api/price-lists/<int:price_list_id>/activate', type='json', auth='user', methods=['POST'], csrf=False)
    def activate_price_list(self, price_list_id, **kwargs):
        """
        API endpoint to activate a price list.
        
        Args:
            price_list_id (int): ID of the price list to activate
        """
        try:
            # Find the price list
            price_list = request.env['pricing.price.list'].browse(price_list_id)
            
            if not price_list.exists():
                return {
                    'status': 'error',
                    'message': 'Price list not found'
                }
            
            # Check permissions
            if not request.env.user.has_group('dashboard_pos.group_pricing_admin'):
                return {
                    'status': 'error',
                    'message': 'Only Pricing Administrators can activate price lists'
                }
            
            # Activate the price list
            result = price_list.action_activate()
            
            return {
                'status': 'success',
                'message': f'Price list "{price_list.name}" has been activated successfully',
                'price_list_id': price_list.id
            }
            
        except Exception as e:
            _logger.error(f"Error in activate_price_list: {e}")
            return {
                'status': 'error',
                'message': f'Internal server error: {str(e)}'
            }
