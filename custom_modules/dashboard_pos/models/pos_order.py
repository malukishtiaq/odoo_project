# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Bhagyadev KP (odoo@cybrosys.com)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
################################################################################
import pytz
import calendar
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)
from datetime import timedelta, datetime, date, time


class PosOrder(models.Model):
    """ Inherited class of pos dashboard to add features of dashboard"""
    _inherit = 'pos.order'

    @api.model
    def get_target(self, monthly_target_input):
        company_id = self.env.company.id
        print('monthly_target_inputmonthly_target_input', monthly_target_input)
        daily_actual = 0
        weekly_actual = 0
        monthly_actual = 0
        today_start = fields.Datetime.to_datetime(fields.Date.today())
        today_end = today_start + timedelta(hours=24)
        pos_order_sale_daily = self.env['pos.order'].search(
            [('date_order', '>=', today_start), ('date_order', '<', today_end)])
        for ord in pos_order_sale_daily:
            daily_actual += ord.amount_total
        today = datetime.today().date()
        year = today.year
        month = today.month
        days_in_month = calendar.monthrange(year, month)[1]
        daily_target = round(int(monthly_target_input) / days_in_month, 2)
        daily_percentage = round((daily_actual / daily_target) * 100, 2)
        date_before_6 = today_start - timedelta(days=6)
        pos_order_sale_weekly = self.env['pos.order'].search(
            [('date_order', '>=', date_before_6), ('date_order', '<', today_end)])
        for ord in pos_order_sale_weekly:
            weekly_actual += ord.amount_total
        weekly_target = daily_target * 7
        weekly_percentage = round((weekly_actual / weekly_target) * 100, 2)
        first_day_of_month = today_start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        pos_order_sale_monthly = self.env['pos.order'].search(
            [('date_order', '>=', first_day_of_month), ('date_order', '<', today_end)])
        for ord in pos_order_sale_monthly:
            monthly_actual += ord.amount_total
        monthly_target = int(monthly_target_input)
        monthly_percentage = round((monthly_actual / monthly_target) * 100, 2)
        return {
            'daily_actual': daily_actual,
            'daily_target': daily_target,
            'daily_percentage': daily_percentage,
            'weekly_actual': round(weekly_actual,2),
            'weekly_target': weekly_target,
            'weekly_percentage': weekly_percentage,
            'monthly_actual': round(monthly_actual,2),
            'monthly_target': monthly_target,
            'monthly_percentage': monthly_percentage,
        }

    @api.model
    def get_all_data(self, from_date_cus, to_date_cus):
        """
        Updated method that uses the comprehensive data source.
        Maintains backward compatibility while providing better data.
        """
        from_date_cus = datetime.strptime(from_date_cus, '%Y-%m-%d').date()
        to_date_cus = datetime.strptime(to_date_cus, '%Y-%m-%d').date()
        
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

    @api.model
    def get_sale_vs_cost(self, option_pos_sales_cost):
        company_id = self.env.company.id
        default_date = datetime.today().date()
        sale_amount = 0
        cost_amount = 0
        profit = 0
        if option_pos_sales_cost == 'pos_today_sales_cost':
            today_start = fields.Datetime.to_datetime(fields.Date.today())
            today_end = today_start + timedelta(hours=24)
            pos_order_sale = self.env['pos.order'].search(
                [('date_order', '>=', today_start), ('date_order', '<', today_end)])
            for sale in pos_order_sale:
                sale_amount += sale.amount_total
            pos_order_cost = self.env['account.move'].search(
                [('state', '=', 'posted'), ('move_type', '=', 'in_invoice'), ('invoice_date', '=', default_date)])
            for cost in pos_order_cost:
                cost_amount += cost.amount_total
            profit = sale_amount - cost_amount
        if option_pos_sales_cost == 'pos_week_sales_cost':
            today_start = fields.Datetime.to_datetime(fields.Date.today())
            today_end = today_start + timedelta(hours=24)
            date_before_6 = today_start - timedelta(days=6)
            date_before_6_date = default_date - timedelta(days=6)
            pos_order_sale = self.env['pos.order'].search(
                [('date_order', '>=', date_before_6), ('date_order', '<', today_end)])
            for sale in pos_order_sale:
                sale_amount += sale.amount_total
            pos_order_cost = self.env['account.move'].search(
                [('state', '=', 'posted'), ('move_type', '=', 'in_invoice'),
                 ('invoice_date', '>=', date_before_6_date)])
            for cost in pos_order_cost:
                cost_amount += cost.amount_total
            profit = sale_amount - cost_amount
        if option_pos_sales_cost == 'pos_month_sales_cost':
            today_start = fields.Datetime.to_datetime(fields.Date.today())
            today_end = today_start + timedelta(hours=24)
            first_day_of_month = today_start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            first_day_of_month_date = default_date.replace(day=1)
            pos_order_sale = self.env['pos.order'].search(
                [('date_order', '>=', first_day_of_month), ('date_order', '<', today_end)])
            for sale in pos_order_sale:
                sale_amount += sale.amount_total
            pos_order_cost = self.env['account.move'].search(
                [('state', '=', 'posted'), ('move_type', '=', 'in_invoice'),
                 ('invoice_date', '>=', first_day_of_month_date)])
            for cost in pos_order_cost:
                cost_amount += cost.amount_total
            profit = sale_amount - cost_amount
        sale_vs_cost = [round(sale_amount, 2), round(cost_amount, 2), round(profit, 2)]
        return sale_vs_cost

    @api.model
    def get_department(self, option):
        """ Function to get the order details of company wise"""
        docs = []
        company_id = self.env.company.id
        default_date = datetime.today().date()
        date_before_6 = default_date - timedelta(days=6)
        if option == 'pos_hourly_sales':

            user_tz = self.env.user.tz if self.env.user.tz else pytz.UTC
            query = '''select  EXTRACT(hour FROM date_order at time zone 'utc' at time zone '{}') 
                       as date_month,sum(amount_total) from pos_order where  
                       EXTRACT(month FROM date_order::date) = EXTRACT(month FROM CURRENT_DATE) 
                       AND pos_order.company_id = ''' + str(
                company_id) + ''' group by date_month '''
            query = query.format(user_tz)
            label = 'HOURS'
        elif option == 'pos_weekly_sales':
            query = '''select  date_order::date as date_month,sum(amount_total) from pos_order where 
             EXTRACT(month FROM date_order::date) = EXTRACT(month FROM CURRENT_DATE) 
            AND DATE(pos_order.date_order) >= ''' + "'" + date_before_6.strftime('%Y-%m-%d') + "'" + '''
            AND DATE(pos_order.date_order) <= ''' + "'" + default_date.strftime('%Y-%m-%d') + "'" + '''
             AND pos_order.company_id = ''' + str(
                company_id) + '''  group by date_month '''
            label = 'DAYS'
            self._cr.execute(query)
            docs = self._cr.dictfetchall()
        else:
            query = '''select TO_CHAR(date_order,'MON')date_month,sum(amount_total) from pos_order where
             EXTRACT(year FROM date_order::date) = EXTRACT(year FROM CURRENT_DATE) AND pos_order.company_id = ''' + str(
                company_id) + ''' group by date_month'''
            label = 'MONTHS'
            self._cr.execute(query)
            docs = self._cr.dictfetchall()
            month_order = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                           'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
            docs = sorted(docs, key=lambda x: month_order.index(x['date_month'].upper()))
        order = []
        for record in docs:
            order.append(record.get('sum'))
        today = []
        for record in docs:
            today.append(record.get('date_month'))
        final = [order, today, label]
        return final

    @api.model
    def get_details(self):
        """ Function to get the payment details"""
        company_id = self.env.company.id
        cr = self._cr
        cr.execute(
            """select pos_payment_method.name ->>'en_US',sum(amount) from pos_payment inner join pos_payment_method on 
            pos_payment_method.id=pos_payment.payment_method_id group by pos_payment_method.name ORDER 
            BY sum(amount) DESC; """)
        payment_details = cr.fetchall()
        cr.execute(
            '''select hr_employee.name,sum(pos_order.amount_paid) as total,count(pos_order.amount_paid) as orders 
            from pos_order inner join hr_employee on pos_order.user_id = hr_employee.user_id 
            where pos_order.company_id =''' + str(
                company_id) + " " + '''GROUP BY hr_employee.name order by total DESC;''')
        salesperson = cr.fetchall()
        total_sales = []
        for rec in salesperson:
            rec = list(rec)
            sym_id = rec[1]
            company = self.env.company
            if company.currency_id.position == 'after':
                rec[1] = "%s %s" % (sym_id, company.currency_id.symbol)
            else:
                rec[1] = "%s %s" % (company.currency_id.symbol, sym_id)
            rec = tuple(rec)
            total_sales.append(rec)
        cr.execute(
            '''select DISTINCT(product_template.name) as product_name,sum(qty) as total_quantity from 
       pos_order_line inner join product_product on product_product.id=pos_order_line.product_id inner join 
       product_template on product_product.product_tmpl_id = product_template.id  where pos_order_line.company_id =''' + str(
                company_id) + ''' group by product_template.id ORDER 
       BY total_quantity DESC Limit 10 ''')
        selling_product = cr.fetchall()
        sessions = self.env['pos.config'].search([])
        sessions_list = []
        dict = {
            'opened': 'Opened',
            'opening_control': "Opening Control"
        }
        for session in sessions:
            st = dict.get(session.pos_session_state)
            if st == None:
                sessions_list.append({
                    'session': session.name,
                    'status': 'Closed'
                })
            else:
                sessions_list.append({
                    'session': session.name,
                    'status': dict.get(session.pos_session_state)
                })
        payments = []
        for rec in payment_details:
            rec = list(rec)
            sym_id = rec[1]
            company = self.env.company
            if company.currency_id.position == 'after':
                rec[1] = "%s %s" % (sym_id, company.currency_id.symbol)
            else:
                rec[1] = "%s %s" % (company.currency_id.symbol, sym_id)
            rec = tuple(rec)
            payments.append(rec)
        return {
            'payment_details': payments,
            'salesperson': total_sales,
            'selling_product': sessions_list,
        }

    @api.model
    def get_refund_details(self):
        """ Function to get the Refund details"""
        default_date = datetime.today().date()
        pos_order = self.env['pos.order'].search([('state', 'in', ['paid', 'done', 'invoiced'])])
        dubai_tz = pytz.timezone('Asia/Dubai')
        utc_tz = pytz.utc

        # Get today's date in Dubai
        today_dubai = datetime.now(dubai_tz).date()

        # Create start and end datetime in Dubai TZ
        start_dt_dubai = dubai_tz.localize(datetime.combine(today_dubai, time.min))
        end_dt_dubai = dubai_tz.localize(datetime.combine(today_dubai, time.max))

        # Convert both to UTC
        start_datetime = start_dt_dubai.astimezone(utc_tz)
        end_datetime = end_dt_dubai.astimezone(utc_tz)

        start_datetime = start_datetime.replace(tzinfo=None)
        end_datetime = end_datetime.replace(tzinfo=None)
        total = 0
        today_refund_total = 0
        total_order_count = 0
        total_refund_count = 0
        new_customer_count = 0
        retained_customer_count = 0
        inactive_customer_count = 0
        today_sale = 0
        today_sale_amount = 0
        a = 0
        for rec in pos_order:
            if rec.amount_total < 0.0 and rec.date_order.date() == default_date:
                today_refund_total = today_refund_total + 1
            total_sales = rec.amount_total
            total = total + total_sales
            total_order_count = total_order_count + 1
            # if rec.date_order.date() == default_date:
            if start_datetime <= rec.date_order <= end_datetime:
                total_sales_today = rec.amount_total
                today_sale_amount = today_sale_amount + total_sales_today
            if start_datetime <= rec.date_order <= end_datetime:
                today_sale = today_sale + 1
            if rec.amount_total < 0.0:
                total_refund_count = total_refund_count + 1

        new_customers = self.env['res.partner'].sudo().search([('company_id', '=', self.env.company.id)])
        for customer in new_customers:
            customer._compute_is_new_customer()
        for cus in new_customers:
            if cus.is_new_customer == 1:
                new_customer_count = new_customer_count + 1
            if cus.is_new_customer > 1:
                retained_customer_count = retained_customer_count + 1
            if cus.inactive_customer:
                inactive_customer_count = inactive_customer_count + 1

        magnitude = 0
        magnitude_tdy = 0
        while abs(total) >= 1000:
            magnitude += 1
            total /= 1000.0
        while abs(today_sale_amount) >= 1000:
            magnitude_tdy += 1
            today_sale_amount /= 1000.0
        # add more suffixes if you need them
        val = '%.2f%s' % (total, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
        val_tdy = '%.2f%s' % (today_sale_amount, ['', 'K', 'M', 'G', 'T', 'P'][magnitude_tdy])
        pos_session = self.env['pos.session'].search([])
        total_session = 0
        for record in pos_session:
            total_session = total_session + 1
        company_id = self.env.company.id
        from_date_cus = default_date
        to_date_cus = default_date
        # Define the SQL query with placeholders
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
        self._cr.execute(query, (company_id, from_date_cus, to_date_cus))
        top_selling_product_pos = self._cr.dictfetchall()
        for t in top_selling_product_pos:
            pdt_tmp_id = self.env['product.template'].browse(t.get('id'))
            available_qty = pdt_tmp_id.qty_available
            t['available_quantity'] = available_qty
            pdt_id = self.env['product.product'].browse(t.get('product'))
            cost = pdt_id.standard_price
            t['cost'] = cost
        query = '''SELECT (product_template.name) AS product_name, product_template.id as id,product_product.id as product,
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
                                           GROUP BY product_template.name, pos_order_line.price_unit,product_template.id,product_product.id
                                           ORDER BY total_quantity ASC 
                                           LIMIT 5'''
        self._cr.execute(query, (company_id, from_date_cus, to_date_cus))
        low_selling_product_pos = self._cr.dictfetchall()
        for t in low_selling_product_pos:
            pdt_tmp_id = self.env['product.template'].browse(t.get('id'))
            available_qty = pdt_tmp_id.qty_available
            t['available_quantity'] = available_qty
            pdt_id = self.env['product.product'].browse(t.get('product'))
            cost = pdt_id.standard_price
            t['cost'] = cost
        query = '''SELECT (product_template.name) AS product_name, product_template.id as id,product_product.id as product,
                                                  SUM(qty) AS total_quantity,
                                                  pos_order_line.price_unit AS price
                                           FROM pos_order_line 
                                           INNER JOIN product_product ON product_product.id = pos_order_line.product_id 
                                           INNER JOIN product_template ON product_product.product_tmpl_id = product_template.id 
                                           INNER JOIN pos_order ON pos_order_line.order_id = pos_order.id
                                           WHERE pos_order_line.company_id = %s 
                                             AND DATE(pos_order.date_order) >= %s 
                                             AND DATE(pos_order.date_order) <= %s 
                                           GROUP BY product_template.name, pos_order_line.price_unit,product_template.id,product_product.id
                                           ORDER BY total_quantity DESC 
                                           LIMIT 5'''
        self._cr.execute(query, (company_id, from_date_cus, to_date_cus))
        top_selling_product_inv = self._cr.dictfetchall()
        for t in top_selling_product_inv:
            pdt_tmp_id = self.env['product.template'].browse(t.get('id'))
            available_qty = pdt_tmp_id.qty_available
            t['available_quantity'] = available_qty
            pdt_id = self.env['product.product'].browse(t.get('product'))
            cost = pdt_id.standard_price
            t['cost'] = cost
        query = '''SELECT product_template.name AS product_name, product_template.id as id,product_product.id as product,
                                          SUM(qty) AS total_quantity,
                                          pos_order_line.price_unit AS price
                                   FROM pos_order_line 
                                   INNER JOIN product_product ON product_product.id = pos_order_line.product_id 
                                   INNER JOIN product_template ON product_product.product_tmpl_id = product_template.id 
                                   INNER JOIN pos_order ON pos_order_line.order_id = pos_order.id
                                   WHERE pos_order_line.company_id = %s 
                                     AND DATE(pos_order.date_order) >= %s 
                                     AND DATE(pos_order.date_order) <= %s 
                                   GROUP BY product_template.name, pos_order_line.price_unit,product_template.id,product_product.id
                                   ORDER BY total_quantity ASC 
                                   LIMIT 5'''
        self._cr.execute(query, (company_id, from_date_cus, to_date_cus))
        low_selling_product_inv = self._cr.dictfetchall()
        for t in low_selling_product_inv:
            pdt_tmp_id = self.env['product.template'].browse(t.get('id'))
            available_qty = pdt_tmp_id.qty_available
            t['available_quantity'] = available_qty
            pdt_id = self.env['product.product'].browse(t.get('product'))
            cost = pdt_id.standard_price
            t['cost'] = cost
        print('top_selling_product_postop_selling_product_pos', top_selling_product_pos)
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
        print('payment_detailspayment_details', payment_details)
        def get_monthly_data(start_date, end_date):
            # Initialize values
            sale_history = 0
            cost_history = 0
            commission_history = 0
            gross_profit_history = 0
            expense_history = 0
            net_income_history = 0

            # Fetch sale history
            sale_history_order = self.env['pos.order'].search(
                [('date_order', '>=', start_date), ('date_order', '<', end_date)])
            for rec in sale_history_order:
                sale_history += rec.amount_total
            sale_history = round(sale_history, 2)

            # Fetch cost history
            cost_history_order = self.env['account.move'].search(
                [('state', '=', 'posted'), ('move_type', '=', 'in_invoice'),
                 ('invoice_date', '>=', start_date), ('invoice_date', '<=', end_date)])
            for cost in cost_history_order:
                cost_history += cost.amount_total

            gross_profit_history = sale_history - cost_history

            # Fetch expense history
            expense_history_order = self.env['account.move.line'].search(
                [('account_id.account_type', '=', 'expense'),
                 ('date', '>=', start_date), ('date', '<=', end_date)])

            for exp in expense_history_order:
                expense_history += exp.debit
            print('expense_historyexpense_history', expense_history)

            net_income_history = sale_history - expense_history

            # Return the dictionary
            return {
                "sale": round(sale_history, 2),
                "cost": round(cost_history, 2),
                "commission": round(commission_history, 2),
                "gross_profit": round(gross_profit_history, 2),
                "expense": round(expense_history, 2),
                "net_income": round(net_income_history, 2)
            }

        def get_month_name(offset_months=0):
            date_obj = datetime.today() - relativedelta(months=offset_months)
            return  date_obj.strftime("%B %Y")

        # Generate data for the last 12 months
        history_data = []
        for i in range(12):
            month_start = fields.Date.today().replace(day=1) - relativedelta(months=i)
            month_end = fields.Date.today().replace(day=1) - relativedelta(months=i - 1,
                                                                           days=1)

            monthly_data = get_monthly_data(month_start, month_end)

            history_data.append({
                "name": get_month_name(i),
                **monthly_data
            })
        print('history_datahistory_datahistory_datahistory_data', history_data)
        return {
            'total_sale': val,
            'today_sale_amount': val_tdy,
            'total_order_count': total_order_count,
            'total_refund_count': total_refund_count,
            'new_customer_count': new_customer_count,
            'retained_customer_count': retained_customer_count,
            'inactive_customer_count': inactive_customer_count,
            'total_session': total_session,
            'today_refund_total': today_refund_total,
            'today_sale': today_sale,
            'top_selling_product_pos': top_selling_product_pos,
            'low_selling_product_pos': low_selling_product_pos,
            'top_selling_product_inv': top_selling_product_inv,
            'low_selling_product_inv': low_selling_product_inv,
            'payment_details': payment_details,
            'history_data': history_data,

        }

    @api.model
    def get_the_top_customer(self, ):
        """ To get the top Customer details"""
        company_id = self.env.company.id
        query = '''select res_partner.name as customer,pos_order.partner_id,sum(pos_order.amount_paid) as amount_total from pos_order 
        inner join res_partner on res_partner.id = pos_order.partner_id where pos_order.company_id = ''' + str(
            company_id) + ''' GROUP BY pos_order.partner_id,
        res_partner.name  ORDER BY amount_total  DESC LIMIT 10;'''
        self._cr.execute(query)
        docs = self._cr.dictfetchall()

        order = []
        for record in docs:
            order.append(record.get('amount_total'))
        day = []
        for record in docs:
            day.append(record.get('customer'))
        final = [order, day]
        return final

    @api.model
    def get_the_top_products(self):
        """ Function to get the top products"""
        company_id = self.env.company.id
        query = '''select DISTINCT(product_template.name)->>'en_US' as product_name,sum(qty) as total_quantity from 
       pos_order_line inner join product_product on product_product.id=pos_order_line.product_id inner join 
       product_template on product_product.product_tmpl_id = product_template.id where pos_order_line.company_id = ''' + str(
            company_id) + ''' group by product_template.id ORDER 
       BY total_quantity DESC Limit 10 '''
        self._cr.execute(query)
        top_product = self._cr.dictfetchall()
        total_quantity = []
        for record in top_product:
            total_quantity.append(record.get('total_quantity'))
        product_name = []
        for record in top_product:
            product_name.append(record.get('product_name'))
        final = [total_quantity, product_name]
        return final

    @api.model
    def get_the_top_categories(self):
        """ Function to get the top Product categories"""
        company_id = self.env.company.id
        query = '''select DISTINCT(product_category.complete_name) as product_category,sum(qty) as total_quantity 
        from pos_order_line inner join product_product on product_product.id=pos_order_line.product_id  inner join 
        product_template on product_product.product_tmpl_id = product_template.id inner join product_category on 
        product_category.id =product_template.categ_id where pos_order_line.company_id = ''' + str(
            company_id) + ''' group by product_category ORDER BY total_quantity DESC '''
        self._cr.execute(query)
        top_product = self._cr.dictfetchall()
        total_quantity = []
        for record in top_product:
            total_quantity.append(record.get('total_quantity'))
        product_categ = []
        for record in top_product:
            product_categ.append(record.get('product_category'))
        final = [total_quantity, product_categ]
        return final

    @api.model
    def get_pricing_scenarios(self, month):
        """
        Compute pricing scenarios for a given month.
        Returns break-even, +10k net, and custom net scenarios.
        """
        try:
            # Parse month (YYYY-MM format)
            year, month_num = map(int, month.split('-'))
            month_start = date(year, month_num, 1)
            if month_num == 12:
                month_end = date(year + 1, 1, 1)
            else:
                month_end = date(year, month_num + 1, 1)
            
            # Check if expenses data is available
            if not self._check_expenses_available(month_start, month_end):
                return {
                    'status': 'insufficient',
                    'message': 'No OPEX available; please close month in Finance.',
                    'month': month
                }
            
            # Get product data for the month
            product_data = self._get_monthly_product_data(month_start, month_end)
            
            if not product_data:
                return {
                    'status': 'insufficient',
                    'message': 'Insufficient sales data for the selected month.',
                    'month': month
                }
            
            # Calculate totals
            totals = self._calculate_totals(product_data, month_start, month_end)
            
            # Check for insufficient sales
            if totals['R'] <= 0:
                return {
                    'status': 'insufficient',
                    'message': 'Insufficient sales last month to compute target.',
                    'month': month
                }
            
            # Calculate scenarios
            scenarios = self._calculate_scenarios(product_data, totals)
            
            return {
                'month': month,
                'totals': totals,
                'scenarios': scenarios,
                'status': 'ok'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error calculating pricing scenarios: {str(e)}',
                'month': month
            }

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

    def _calculate_totals(self, product_data, month_start, month_end):
        """Calculate R, G, E, N totals"""
        R = sum(item['qty'] * item['price'] for item in product_data)
        G = sum(item['qty'] * (item['price'] - item['cost']) for item in product_data)
        
        # Get monthly expenses (OPEX - exclude COGS & VAT)
        E = self._get_monthly_expenses(month_start, month_end)
        
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

    def _get_monthly_expenses(self, month_start, month_end):
        """Get monthly OPEX expenses from GL accounts"""
        company_id = self.env.company.id
        
        # Query to get OPEX expenses from GL entries
        # Exclude COGS, VAT, Income Tax, and Extraordinary items
        query = '''
            SELECT COALESCE(SUM(aml.debit - aml.credit), 0) AS expenses_E
            FROM account_move_line aml
            INNER JOIN account_account aa ON aa.id = aml.account_id
            INNER JOIN account_move am ON am.id = aml.move_id
            WHERE aml.company_id = %s
                AND aml.date >= %s
                AND aml.date < %s
                AND am.state = 'posted'
                AND aa.account_type IN ('expense', 'other')
                AND aa.code NOT LIKE '4%'  -- Exclude COGS (typically 4xxx)
                AND aa.code NOT LIKE '5%'  -- Exclude VAT accounts (typically 5xxx)
                AND aa.name NOT ILIKE '%vat%'
                AND aa.name NOT ILIKE '%tax%'
                AND aa.name NOT ILIKE '%extraordinary%'
                AND aa.name NOT ILIKE '%cogs%'
                AND aa.name NOT ILIKE '%cost of goods%'
        '''
        
        self._cr.execute(query, (company_id, month_start, month_end))
        result = self._cr.fetchone()
        
        expenses_E = result[0] if result and result[0] else 0.0
        
        # Clamp to 0 if negative (shouldn't happen for expenses)
        if expenses_E < 0:
            _logger.warning(f"Negative expenses detected for {month_start}: {expenses_E}. Clamping to 0.")
            expenses_E = 0.0
            
        return round(expenses_E, 2)

    def _check_expenses_available(self, month_start, month_end):
        """Check if OPEX data is available for the month"""
        company_id = self.env.company.id
        
        query = '''
            SELECT COUNT(*) as count
            FROM account_move_line aml
            INNER JOIN account_account aa ON aa.id = aml.account_id
            INNER JOIN account_move am ON am.id = aml.move_id
            WHERE aml.company_id = %s
                AND aml.date >= %s
                AND aml.date < %s
                AND am.state = 'posted'
                AND aa.account_type IN ('expense', 'other')
        '''
        
        self._cr.execute(query, (company_id, month_start, month_end))
        result = self._cr.fetchone()
        
        return result[0] > 0 if result else False

    def _convert_to_net_prices(self, raw_data):
        """Convert gross prices to net prices using VAT rates"""
        # Default UAE VAT rate
        default_vat_rate = 0.05
        
        for item in raw_data:
            # Get VAT rate for the product
            vat_rate = self._get_product_vat_rate(item['product_name'])
            
            # Convert price to net (assuming input is gross)
            if item['price'] > 0:
                item['price'] = item['price'] / (1 + vat_rate)
            
            # Convert cost to net (assuming input is gross)
            if item['cost'] > 0:
                item['cost'] = item['cost'] / (1 + vat_rate)
        
        return raw_data

    def _get_product_vat_rate(self, product_name):
        """Get VAT rate for a product"""
        try:
            # Try to get VAT rate from product template
            product_template = self.env['product.template'].search([
                ('name', '=', product_name),
                ('available_in_pos', '=', True)
            ], limit=1)
            
            if product_template and product_template.taxes_id:
                # Get the first active VAT tax
                vat_tax = product_template.taxes_id.filtered(
                    lambda t: t.type_tax_use == 'sale' and 
                             t.amount_type == 'percent' and 
                             t.active
                )
                if vat_tax:
                    return vat_tax[0].amount / 100
            
            # Default to UAE VAT rate
            return 0.05
            
        except Exception as e:
            _logger.warning(f"Error getting VAT rate for {product_name}: {e}")
            return 0.05

    def _calculate_scenarios(self, product_data, totals):
        """Calculate all pricing scenarios"""
        scenarios = {}
        
        # Break-even scenario
        scenarios['break_even'] = self._calculate_break_even(product_data, totals)
        
        # Net +10k scenario
        scenarios['net_10k'] = self._calculate_net_target(product_data, totals, 10000)
        
        # Net custom scenario (placeholder - will be calculated with user input)
        scenarios['net_custom'] = {
            'target': 0,
            'status': 'pending',
            'message': 'Enter custom target amount',
            'uniform': None,
            'weighted': None
        }
        
        return scenarios

    def _calculate_break_even(self, product_data, totals):
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

    def _calculate_net_target(self, product_data, totals, target_net):
        """Calculate net target scenarios (uniform and weighted)"""
        N_target = target_net
        x_raw = (N_target - totals['N']) / totals['R'] if totals['R'] > 0 else 0
        
        # Check if unrealistic
        unrealistic = self._check_unrealistic(x_raw, product_data, totals, N_target)
        
        # Apply cost floor
        x = max(x_raw, totals['x_min'])
        
        # Uniform scenario
        uniform = self._calculate_uniform_uplift(product_data, x)
        
        # Weighted scenario
        weighted = self._calculate_weighted_uplift(product_data, totals, x)
        
        return {
            'uniform': {
                'x': round(x, 4),
                'rows': uniform,
                'unrealistic': unrealistic
            },
            'weighted': {
                'x_budget': round(x, 4),
                'x_range': [round(min(row['pct'] for row in weighted), 2), 
                           round(max(row['pct'] for row in weighted), 2)],
                'rows': weighted,
                'unrealistic': unrealistic
            }
        }

    def _check_unrealistic(self, x_raw, product_data, totals, N_target):
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

    def _calculate_uniform_uplift(self, product_data, x):
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

    def _calculate_weighted_uplift(self, product_data, totals, x_budget):
        """Calculate weighted uplift scenario"""
        # Calculate weights
        weights = []
        for item in product_data:
            revenue = item['qty'] * item['price']
            weight = revenue / totals['R'] if totals['R'] > 0 else 0
            weights.append(weight)
        
        # Calculate S2 (sum of squared weights)
        S2 = sum(w**2 for w in weights)
        
        # Initial per-item uplifts
        x_items = []
        for i, item in enumerate(product_data):
            x_i = x_budget * (weights[i] / S2) if S2 > 0 else 0
            # Apply cost floor
            cost_floor = (item['cost'] / item['price']) - 1 if item['price'] > 0 else 0
            x_i = max(x_i, cost_floor)
            x_items.append(x_i)
        
        # Iterative re-normalization to maintain budget
        max_iterations = 20
        tolerance = 0.01
        
        for iteration in range(max_iterations):
            # Calculate current total uplift
            current_total = sum(x_items[i] * item['qty'] * item['price'] for i, item in enumerate(product_data))
            target_total = x_budget * totals['R']
            
            if abs(current_total - target_total) < tolerance:
                break
            
            # Redistribute remaining budget
            remaining_budget = target_total - current_total
            if abs(remaining_budget) < tolerance:
                break
            
            # Find items with headroom (not at cost floor)
            headroom_items = []
            for i, item in enumerate(product_data):
                cost_floor = (item['cost'] / item['price']) - 1 if item['price'] > 0 else 0
                if x_items[i] > cost_floor + 0.001:  # Small tolerance
                    headroom_items.append(i)
            
            if not headroom_items:
                break
            
            # Redistribute proportionally by weight
            total_headroom_weight = sum(weights[i] for i in headroom_items)
            if total_headroom_weight > 0:
                for i in headroom_items:
                    adjustment = (remaining_budget * weights[i]) / (total_headroom_weight * item['qty'] * item['price'])
                    x_items[i] += adjustment
                    
                    # Re-apply cost floor
                    cost_floor = (product_data[i]['cost'] / product_data[i]['price']) - 1 if product_data[i]['price'] > 0 else 0
                    x_items[i] = max(x_items[i], cost_floor)
        
        # Generate weighted data
        weighted_data = []
        for i, item in enumerate(product_data):
            price_target = item['price'] * (1 + x_items[i])
            pct_change = x_items[i] * 100
            margin_after = ((price_target - item['cost']) / price_target) * 100 if price_target > 0 else 0
            
            weighted_data.append({
                'product': item['product_name'],
                'qty': round(item['qty'], 2),
                'cost': round(item['cost'], 2),
                'price_real': round(item['price'], 2),
                'price_target': round(price_target, 2),
                'pct': round(pct_change, 2),
                'margin_after': round(margin_after, 2)
            })
        
        return weighted_data

    @api.model
    def apply_pricing_scenarios(self, month, scenario, mode, target=None, dry_run=True, idempotency_key=None):
        """
        Apply pricing scenarios to create a price list
        
        Args:
            month (str): Month in YYYY-MM format
            scenario (str): 'break_even', 'net_10k', or 'net_custom'
            mode (str): 'uniform' or 'weighted'
            target (float): Target amount for custom scenarios
            dry_run (bool): If True, only preview; if False, create price list
            idempotency_key (str): UUID to prevent duplicate requests
        
        Returns:
            dict: Price list creation result
        """
        try:
            # Check for existing price list with same idempotency key
            if idempotency_key:
                existing = self.env['pricing.price.list'].search([
                    ('name', 'ilike', idempotency_key)
                ], limit=1)
                if existing:
                    return {
                        'price_list_id': existing.id,
                        'status': existing.status,
                        'message': 'Price list already exists with this idempotency key'
                    }
            
            # Get pricing scenarios data
            scenarios_data = self.get_pricing_scenarios(month)
            if scenarios_data['status'] != 'ok':
                return {
                    'status': 'error',
                    'message': scenarios_data['message']
                }
            
            # Get the appropriate scenario data
            if scenario == 'break_even':
                scenario_data = scenarios_data['scenarios']['break_even']
                target_amount = 0
            elif scenario == 'net_10k':
                scenario_data = scenarios_data['scenarios']['net_10k'][mode]['rows']
                target_amount = 10000
            elif scenario == 'net_custom':
                if not target:
                    return {
                        'status': 'error',
                        'message': 'Target amount is required for custom scenarios'
                    }
                # Calculate custom scenario
                custom_result = self.calculate_custom_net_scenario(month, target)
                if custom_result['status'] != 'ok':
                    return custom_result
                scenario_data = custom_result['scenarios'][mode]['rows']
                target_amount = target
            else:
                return {
                    'status': 'error',
                    'message': 'Invalid scenario type'
                }
            
            # Create price list items
            price_items = []
            for item in scenario_data:
                if scenario == 'break_even':
                    old_price = item['price_real']
                    new_price = item['price_target']
                    pct_change = item['diff_pct'] / 100
                    floor_applied = new_price <= item['cost']
                else:
                    old_price = item['price_real']
                    new_price = item['price_target']
                    pct_change = item['pct'] / 100
                    floor_applied = new_price <= item['cost']
                
                price_items.append({
                    'product_name': item['product'],
                    'old_price': old_price,
                    'new_price': new_price,
                    'pct_change': pct_change,
                    'floor_applied': floor_applied
                })
            
            if dry_run:
                # Return preview only
                return {
                    'status': 'preview',
                    'summary': {
                        'products': len(price_items),
                        'min_pct': min(item['pct_change'] for item in price_items),
                        'max_pct': max(item['pct_change'] for item in price_items),
                        'floors_triggered': len([item for item in price_items if item['floor_applied']])
                    },
                    'rows_sample': price_items[:10]  # First 10 items as sample
                }
            else:
                # Create actual price list
                price_list_name = f"{scenario}_{mode}_{month}_{target_amount if target else 'auto'}"
                if idempotency_key:
                    price_list_name += f"_{idempotency_key[:8]}"
                
                price_list = self.env['pricing.price.list'].create({
                    'name': price_list_name,
                    'month_key': month,
                    'source_scenario': scenario,
                    'mode': mode,
                    'target': target_amount,
                    'status': 'draft'
                })
                
                # Create price list items
                for item in price_items:
                    self.env['pricing.price.list.item'].create({
                        'price_list_id': price_list.id,
                        'product_name': item['product_name'],
                        'old_price': item['old_price'],
                        'new_price': item['new_price'],
                        'pct_change': item['pct_change'],
                        'floor_applied': item['floor_applied']
                    })
                
                return {
                    'price_list_id': price_list.id,
                    'status': 'draft',
                    'summary': {
                        'products': len(price_items),
                        'min_pct': min(item['pct_change'] for item in price_items),
                        'max_pct': max(item['pct_change'] for item in price_items),
                        'floors_triggered': len([item for item in price_items if item['floor_applied']])
                    },
                    'rows_sample': price_items[:10]
                }
                
        except Exception as e:
            _logger.error(f"Error applying pricing scenarios: {e}")
            return {
                'status': 'error',
                'message': f'Error applying pricing scenarios: {str(e)}'
            }

    @api.model
    def calculate_custom_net_scenario(self, month, custom_target):
        """Calculate custom net target scenario"""
        try:
            # Get existing data
            scenarios_data = self.get_pricing_scenarios(month)
            
            if scenarios_data['status'] != 'ok':
                return scenarios_data
            
            product_data = self._get_monthly_product_data(
                datetime.strptime(month, '%Y-%m').date().replace(day=1),
                (datetime.strptime(month, '%Y-%m').date().replace(day=1) + relativedelta(months=1))
            )
            
            totals = scenarios_data['totals']
            N_target = float(custom_target)
            
            # Calculate custom scenario
            custom_scenario = self._calculate_net_target(product_data, totals, N_target)
            
            return {
                'month': month,
                'totals': totals,
                'scenarios': {
                    'net_custom': {
                        'target': N_target,
                        'status': 'ok',
                        'message': '',
                        'uniform': custom_scenario['uniform'],
                        'weighted': custom_scenario['weighted']
                    }
                },
                'status': 'ok'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error calculating custom scenario: {str(e)}',
                'month': month
            }

    @api.model
    def get_pricing_scenarios_date_range(self, start_date, end_date):
        """
        Get pricing scenarios for a specific date range.
        Similar to get_pricing_scenarios but for custom date ranges.
        
        Args:
            start_date: Start date (date object)
            end_date: End date (date object)
            
        Returns:
            dict: Pricing scenarios data for the date range
        """
        try:
            from datetime import datetime, timedelta
            
            # Convert dates to datetime for database queries
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            # Get product data for the date range
            product_data = self._get_date_range_product_data(start_datetime, end_datetime)
            
            if not product_data:
                return {
                    'status': 'insufficient',
                    'message': 'No sales data found for the selected date range',
                    'data': []
                }
            
            # Calculate totals for the date range
            totals = self._calculate_totals_date_range(product_data, start_datetime, end_datetime)
            
            # Check if expenses are available
            expenses_available = self._check_expenses_available_date_range(start_datetime, end_datetime)
            
            if not expenses_available:
                return {
                    'status': 'insufficient',
                    'message': 'Operating expenses not available for the selected date range. Please ensure the Finance month is closed.',
                    'data': []
                }
            
            # Calculate pricing scenarios
            scenarios = self._calculate_pricing_scenarios(product_data, totals)
            
            return {
                'status': 'success',
                'data': scenarios,
                'totals': totals,
                'date_range': {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d')
                }
            }
            
        except Exception as e:
            _logger.error(f"Error calculating pricing scenarios for date range {start_date} to {end_date}: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error calculating pricing scenarios: {str(e)}',
                'data': []
            }

    def _get_date_range_product_data(self, start_datetime, end_datetime):
        """
        Get product data for a specific date range.
        
        Args:
            start_datetime: Start datetime
            end_datetime: End datetime
            
        Returns:
            list: Product data for the date range
        """
        try:
            # Query POS order lines for the date range
            query = """
                SELECT 
                    pol.product_id,
                    pt.name as product_name,
                    SUM(pol.qty) as total_qty,
                    AVG(pol.price_unit) as avg_price,
                    AVG(pol.total_cost) as avg_cost
                FROM pos_order_line pol
                JOIN pos_order po ON pol.order_id = po.id
                JOIN product_product pp ON pol.product_id = pp.id
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                WHERE po.date_order >= %s
                    AND po.date_order <= %s
                    AND po.state IN ('paid', 'done', 'invoiced')
                    AND po.company_id = %s
                GROUP BY pol.product_id, pt.name
                HAVING SUM(pol.qty) > 0
                ORDER BY SUM(pol.qty * pol.price_unit) DESC
            """
            
            self.env.cr.execute(query, (start_datetime, end_datetime, self.env.company.id))
            results = self.env.cr.fetchall()
            
            product_data = []
            for row in results:
                product_id, product_name, qty, price, cost = row
                product_data.append({
                    'product_id': product_id,
                    'product_name': product_name,
                    'qty': float(qty) if qty is not None else 0.0,
                    'price': float(price) if price is not None else 0.0,
                    'cost': float(cost) if cost is not None else 0.0
                })
            
            # Convert to net prices (pre-VAT)
            product_data = self._convert_to_net_prices(product_data)
            
            return product_data
            
        except Exception as e:
            _logger.error(f"Error getting product data for date range: {str(e)}")
            return []

    def _calculate_totals_date_range(self, product_data, start_datetime, end_datetime):
        """
        Calculate totals for a date range.
        
        Args:
            product_data: List of product data
            start_datetime: Start datetime
            end_datetime: End datetime
            
        Returns:
            dict: Calculated totals
        """
        try:
            # Calculate revenue and gross profit
            R = sum(item['qty'] * item['price'] for item in product_data)
            G = sum(item['qty'] * item['cost'] for item in product_data)
            
            # Get monthly expenses for the date range
            E = self._get_date_range_expenses(start_datetime, end_datetime)
            
            # Calculate net income and minimum uplift
            N = R - G - E
            x_min = E / R if R > 0 else 0
            
            return {
                'revenue': R,
                'gross_profit': G,
                'expenses': E,
                'net_income': N,
                'min_uplift': x_min
            }
            
        except Exception as e:
            _logger.error(f"Error calculating totals for date range: {str(e)}")
            return {
                'revenue': 0,
                'gross_profit': 0,
                'expenses': 0,
                'net_income': 0,
                'min_uplift': 0
            }

    def _get_date_range_expenses(self, start_datetime, end_datetime):
        """
        Get operating expenses for a date range.
        
        Args:
            start_datetime: Start datetime
            end_datetime: End datetime
            
        Returns:
            float: Total operating expenses for the date range
        """
        try:
            # Query account move lines for operating expenses
            query = """
                SELECT COALESCE(SUM(aml.debit - aml.credit), 0) as total_expenses
                FROM account_move_line aml
                JOIN account_account aa ON aml.account_id = aa.id
                WHERE aml.date >= %s
                    AND aml.date <= %s
                    AND aml.company_id = %s
                    AND aa.code NOT LIKE '4%'  -- Exclude COGS
                    AND aa.code NOT LIKE '5%'  -- Exclude VAT
                    AND (aa.code LIKE '6%' OR aa.code LIKE '7%')  -- Operating expenses
            """
            
            self.env.cr.execute(query, (start_datetime.date(), end_datetime.date(), self.env.company.id))
            result = self.env.cr.fetchone()
            
            expenses = float(result[0]) if result and result[0] else 0.0
            
            # Clamp negative expenses to 0
            return max(0.0, expenses)
            
        except Exception as e:
            _logger.error(f"Error getting expenses for date range: {str(e)}")
            return 0.0

    def _check_expenses_available_date_range(self, start_datetime, end_datetime):
        """
        Check if operating expenses are available for a date range.
        
        Args:
            start_datetime: Start datetime
            end_datetime: End datetime
            
        Returns:
            bool: True if expenses are available
        """
        try:
            query = """
                SELECT COUNT(*)
                FROM account_move_line aml
                JOIN account_account aa ON aml.account_id = aa.id
                WHERE aml.date >= %s
                    AND aml.date <= %s
                    AND aml.company_id = %s
                    AND aa.code NOT LIKE '4%'  -- Exclude COGS
                    AND aa.code NOT LIKE '5%'  -- Exclude VAT
                    AND (aa.code LIKE '6%' OR aa.code LIKE '7%')  -- Operating expenses
            """
            
            self.env.cr.execute(query, (start_datetime.date(), end_datetime.date(), self.env.company.id))
            result = self.env.cr.fetchone()
            
            return result and result[0] > 0
            
        except Exception as e:
            _logger.error(f"Error checking expenses availability for date range: {str(e)}")
            return False

    @api.model
    def get_complete_monthly_sales_data(self, month_start, month_end):
        """
        Get complete list of all products sold in a month with prices and quantities.
        
        This method provides comprehensive monthly sales data for all products,
        replacing the limited get_all_data() method.
        
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
            import json
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

    def _export_to_excel(self, data):
        """Export data to Excel format."""
        try:
            import xlsxwriter
            import io
            
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Monthly Sales Data')
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D7E4BC',
                'border': 1
            })
            
            currency_format = workbook.add_format({'num_format': '0.00'})
            percentage_format = workbook.add_format({'num_format': '0.00%'})
            
            # Write headers
            headers = [
                'Product Name', 'SKU', 'Category', 'Total Quantity', 'Sale Quantity', 'Return Quantity',
                'Order Count', 'Days Sold', 'Avg Daily Sales', 'Avg Price', 'Min Price', 'Max Price',
                'Price StdDev', 'Price Consistency', 'Total Revenue', 'Avg Cost', 'Total Cost',
                'Standard Cost', 'List Price', 'Margin Amount', 'Margin %', 'Current Stock',
                'Turnover Ratio', 'POS Available', 'Sale OK', 'Purchase OK'
            ]
            
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
            
            # Write data
            for row, product in enumerate(data['products'], 1):
                worksheet.write(row, 0, product['product_name'])
                worksheet.write(row, 1, product['sku'])
                worksheet.write(row, 2, product['category_name'])
                worksheet.write(row, 3, product['total_quantity'])
                worksheet.write(row, 4, product['sale_quantity'])
                worksheet.write(row, 5, product['return_quantity'])
                worksheet.write(row, 6, product['order_count'])
                worksheet.write(row, 7, product['days_sold'])
                worksheet.write(row, 8, product['avg_daily_sales'])
                worksheet.write(row, 9, product['avg_price'], currency_format)
                worksheet.write(row, 10, product['min_price'], currency_format)
                worksheet.write(row, 11, product['max_price'], currency_format)
                worksheet.write(row, 12, product['price_stddev'])
                worksheet.write(row, 13, product['price_consistency'])
                worksheet.write(row, 14, product['total_revenue'], currency_format)
                worksheet.write(row, 15, product['avg_cost'], currency_format)
                worksheet.write(row, 16, product['total_cost'], currency_format)
                worksheet.write(row, 17, product['standard_cost'], currency_format)
                worksheet.write(row, 18, product['list_price'], currency_format)
                worksheet.write(row, 19, product['margin_amount'], currency_format)
                worksheet.write(row, 20, product['margin_percentage'] / 100, percentage_format)
                worksheet.write(row, 21, product['current_stock'])
                worksheet.write(row, 22, product['turnover_ratio'])
                worksheet.write(row, 23, 'Yes' if product['pos_available'] else 'No')
                worksheet.write(row, 24, 'Yes' if product['sale_ok'] else 'No')
                worksheet.write(row, 25, 'Yes' if product['purchase_ok'] else 'No')
            
            # Auto-fit columns
            for col in range(len(headers)):
                worksheet.set_column(col, col, 15)
            
            workbook.close()
            output.seek(0)
            return output.getvalue()
            
        except ImportError:
            _logger.warning("xlsxwriter not available, falling back to CSV export")
            return self._export_to_csv(data)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        res.company_id = self.env.company.id
        return res

    is_new_customer = fields.Integer(string='POS Order Count(Today)', compute="_compute_is_new_customer", store=True)
    inactive_customer = fields.Boolean(string='Inactive Customer')

    @api.depends('pos_order_count')
    def _compute_is_new_customer(self):
        partners = self.env['res.partner'].sudo().search([('company_id', '=', self.env.company.id)])
        today_start = fields.Datetime.to_datetime(fields.Date.today())
        today_end = today_start + timedelta(hours=24)
        for partner in partners:
            # pos_order = self.env['pos.order'].sudo().search([('partner_id', '=', partner.id),
            #                                                  ('date_order','>=', today_start),
            #                                                  ('date_order','<', today_end),
            #                                                  ('company_id', '=', self.env.company.id),
            #                                                  ])
            pos_order = self.env['pos.order'].sudo().search([('partner_id', '=', partner.id),
                                                             ('company_id', '=', self.env.company.id),
                                                             ])
            partner.is_new_customer = len(pos_order)
            six_months_before = today_start - relativedelta(months=6)
            pos_order_inactive = self.env['pos.order'].sudo().search([('partner_id', '=', partner.id),
                                                                      ('date_order', '>=', six_months_before),
                                                                      ('date_order', '<', today_end),
                                                                      ('company_id', '=', self.env.company.id),
                                                                      ])
            if pos_order_inactive:
                partner.inactive_customer = False
            else:
                partner.inactive_customer = True

