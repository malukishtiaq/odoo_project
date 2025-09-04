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
        from_date_cus = datetime.strptime(from_date_cus, '%Y-%m-%d').date()
        to_date_cus = datetime.strptime(to_date_cus, '%Y-%m-%d').date()
        company_id = self.env.company.id
        from_date_cus = datetime.strptime(str(from_date_cus), '%Y-%m-%d').date()
        to_date_cus = datetime.strptime(str(to_date_cus), '%Y-%m-%d').date()

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
                               GROUP BY product_template.name,pos_order_line.price_unit,product_template.id,product_product.id
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
        print('payment_detailspayment_detailsccccccccccccccc',payment_details)

        return {
            'top_selling_product_pos': top_selling_product_pos,
            'top_selling_product_inv': top_selling_product_inv,
            'low_selling_product_pos': low_selling_product_pos,
            'low_selling_product_inv': low_selling_product_inv,
            'payment_details': payment_details,
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
