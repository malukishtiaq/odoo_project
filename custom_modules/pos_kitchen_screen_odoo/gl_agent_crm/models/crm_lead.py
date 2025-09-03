# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import requests
import xmlrpc.client


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    module_line_ids = fields.One2many('lead.module.selector', 'lead_id')
    modules_total_amt = fields.Monetary(string='Total Amount', compute='total_amount', tracking=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    is_submitted_approval = fields.Boolean(default=False)
    is_manager_approval = fields.Boolean(default=False)
    is_first_approved = fields.Boolean(default=False)
    is_second_approved = fields.Boolean(default=False)
    is_approved = fields.Boolean(default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Sales Manager Approval'),
        ('pending_manager_approval', 'Pending Manager Approval '),
        ('approved', 'Approved'),
        ('reject', 'Rejected'),
        ('cancel', 'Cancel')
    ], default='draft', tracking=True)
    upload_trade_licence = fields.Binary(string="Trade Licence")
    upload_vat_certificate = fields.Binary(string="VAT Certificate")
    upload_data_sheet = fields.Binary(string="Data Sheet")
    upload_company_logo = fields.Binary(string="Company  Logo")
    filename_1 = fields.Char(string="Trade Licence")
    filename_2 = fields.Char(string="VAT Certificate")
    filename_3 = fields.Char(string="Data Sheet")
    filename_4 = fields.Char(string="Company  Logo")
    lead_old_id = fields.Char()

    def migrate_lead_data(self):
        url = "https://class.glsystem.ae/"
        db = "Class_test1"
        username = "admin"
        password = "Mo@sU@135"

        session = requests.Session()
        login_url = f"{url}/web/session/authenticate"
        payload = {
            "jsonrpc": "2.0",
            "params": {
                "db": db,
                "login": username,
                "password": password
            }
        }

        res = session.post(login_url, json=payload)
        result = res.json()
        if res.ok and 'result' in result and result['result'].get('uid'):
            search_read_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "model": "crm.lead",
                    "method": "search_read",
                    "args": [
                        [],
                        ['id', 'name', 'email_from', 'phone', 'user_id', 'stage_id', 'team_id',
                         'partner_id', 'description', 'date_deadline', 'priority', 'tag_ids',
                         'partner_name', 'city', 'lang_id', 'expected_revenue', 'probability',
                         'website', 'campaign_id', 'referred', 'medium_id', 'source_id', 'lost_reason_id']  # Fields to fetch
                    ],
                    "kwargs": {
                        "limit": 10
                    }
                }
            }

            # Post the request to get leads

            rpc_url = f"{url}/web/dataset/call_kw"
            res = session.post(rpc_url, json=search_read_payload)
            leads_result = res.json()

            if 'result' in leads_result:
                leads = leads_result['result']
                for lead in leads:
                    sales_person = self.env['res.users'].search([('name', '=', lead['user_id'][1])])
                    partner_id = self.env['res.partner'].search([('name','=', lead['partner_id'][1])])
                    stage_id = self.env['crm.stage'].search([('name','=', lead['stage_id'][1])])
                    team_id = self.env['crm.team'].search([('name','=', lead['team_id'][1])])
                    lang_id = self.env['res.lang'].search([('name','=', lead['lang_id'][1])])
                    campaign_id = self.env['utm.campaign'].search([('name','=', lead['campaign_id'][1])])
                    medium_id = self.env['utm.medium'].search([('name','=', lead['medium_id'][1])])
                    source_id = self.env['utm.source'].search([('name','=', lead['source_id'][1])])
                    lost_reason = self.env['crm.lost.reason'].search([('name', '=', lead['lost_reason_id'][1])])
                    new_lead = self.env['crm.lead'].create({
                        'type': 'opportunity',
                        'lead_old_id': lead['id'],
                        'name': lead['name'],
                        'email_from': lead['email_from'],
                        'phone': lead['phone'],
                        'user_id': sales_person.id if lead['user_id'] else False,
                        'partner_id': partner_id.id if lead['partner_id'] else False,
                        'stage_id': stage_id.id if lead['stage_id'] else False,
                        'team_id': team_id.id if lead['team_id'] else False,
                        'description': lead['description'],
                        'date_deadline': lead['date_deadline'],
                        'priority': lead['priority'],
                        'tag_ids': lead['tag_ids'],
                        'partner_name': lead['partner_name'],
                        'city': lead['city'],
                        'lang_id': lang_id.id,
                        'referred': lead['referred'],
                        'expected_revenue': lead['expected_revenue'],
                        'probability': lead['probability'],
                        'website': lead['website'],
                        'campaign_id': campaign_id.id,
                        'medium_id': medium_id.id,
                        'source_id': source_id.id,
                        'lost_reason_id': lost_reason.id
                    })

                    # data = {
                    #     "jsonrpc": "2.0",
                    #     "method": "call",
                    #     "params": {
                    #         "model": "mail.message",
                    #         "method": "search_read",
                    #         "args": [
                    #             [
                    #                 ('model', '=', 'crm.lead'),
                    #                 ('res_id', '=', lead.id)
                    #             ],
                    #             ['id', 'subject', 'body', 'date', 'author_id']
                    #         ],
                    #         "kwargs": {
                    #             "limit": 10,
                    #             "order": "date desc"
                    #         }
                    #     }
                    # }
                    #
                    # res = session.post(rpc_url, json=data)
                    # messages = res.json().get('result', [])
                    #
                    # for msg in messages:
                    #     print(f"🟡 {msg['date']} - {msg['author_id'][1]}:\n{msg['body']}\n")
                    # for msg in messages:
                    #     new_res_id = lead_id_map.get(msg['res_id'])
                    #     if new_res_id:
                    #         env['mail.message'].create({
                    #             'res_id': new_res_id,
                    #             'model': 'crm.lead',
                    #             'author_id': msg['author_id'][0] if msg['author_id'] else False,
                    #             'body': msg['body'],
                    #             'message_type': msg['message_type'],
                    #             'subtype_id': msg['subtype_id'][0] if msg['subtype_id'] else False,
                    #             'date': msg['date'],
                    #         })
            else:
                print("❌ Failed to fetch leads:", leads_result)
        else:
            print("❌ Login failed:", result)
            exit()

        # for msg in messages:
        #     new_res_id = lead_id_map.get(msg['res_id'])
        #     if new_res_id:
        #         env['mail.message'].create({
        #             'res_id': new_res_id,
        #             'model': 'crm.lead',
        #             'author_id': msg['author_id'][0] if msg['author_id'] else False,
        #             'body': msg['body'],
        #             'message_type': msg['message_type'],
        #             'subtype_id': msg['subtype_id'][0] if msg['subtype_id'] else False,
        #             'date': msg['date'],
        #         })

    def cancel(self):
        for record in self:
            record.state = 'cancel'

    def reset_to_draft(self):
        for record in self:
            record.state = 'draft'
            record.is_submitted_approval = False

    def submit_for_approval(self):
        for record in self:
            record.is_submitted_approval = True
            record.state = 'pending_approval'

    def submit_for_manager_approval(self):
        for record in self:
            record.is_manager_approval = True
            record.state = 'pending_manager_approval'

    def first_approval(self):
        for record in self:
            record.is_submitted_approval =  False
            record.is_approved = True
            record.state = 'approved'

    def second_approval(self):
        for record in self:
            record.is_manager_approval = False
            record.is_approved = True
            record.state = 'approved'

    def reject(self):
        return{
            'type': 'ir.actions.act_window',
            'name': 'Reject Reason',
            'res_model': 'reject.approval.wizard',
            'view_mode': 'form',
            'target': 'new',
            # 'views': [(self.env.ref('gl_agent_crm.reject_approval_wizard_form_view').id, 'form')],
            # 'context': {'default_name': 'Hello from main record'},
        }

    @api.depends('module_line_ids.module_id')
    def total_amount(self):
        total_amt = 0
        self.modules_total_amt = 0
        for line in self.module_line_ids:
            total_amt += line.price_unit
            self.modules_total_amt = total_amt

class LeadModuleSelector(models.Model):
    _name = 'lead.module.selector'
    _description = 'Lead Module Selector'

    lead_id = fields.Many2one('crm.lead')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    module_id = fields.Many2one('module.price.configurator', string='Module')
    price_unit = fields.Monetary(string='Price', related='module_id.price_unit')


class RejectionReason(models.Model):
    _name = 'rejection.reason'
    _description = 'Rejection Reason'
    _rec_name = 'name'

    name = fields.Char(string='Rejection Reason')
