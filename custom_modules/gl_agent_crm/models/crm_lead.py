# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import requests
import xmlrpc.client
import traceback
import logging

_logger = logging.getLogger(__name__)

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

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get('is_old_message'):
            # Do not post any default messages
            return super(CrmLead, self.with_context(mail_create_nolog=True, mail_create_nosubscribe=True)).create(
                vals_list)
        return super(CrmLead, self).create(vals_list)

    def migrate_lead_data(self):
        url = "https://class.glsystem.ae"
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
        if 'result' in result and result['result'].get('uid'):
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
                         'website', 'campaign_id', 'referred', 'medium_id', 'source_id',
                         'lost_reason']  # Fields to fetch
                    ],
                    "kwargs": {
                        # "limit":
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
                    tag_ids = lead.get('tag_ids', [])
                    if tag_ids:
                        search_read_payload = {
                            "jsonrpc": "2.0",
                            "method": "call",
                            "params": {
                                "model": "crm.tag",
                                "method": "search_read",
                                "args": [
                                    [('id', 'in', tag_ids)],
                                    ['name']  # Fields to fetch
                                ],
                                "kwargs": {
                                    # Optional: "limit": 25
                                }
                            }
                        }

                        rpc_url = f"{url}/web/dataset/call_kw"
                        res = session.post(rpc_url, json=search_read_payload)
                        result_json = res.json()

                        if 'result' in result_json:
                            tag_names = [tag['name'] for tag in result_json['result']]
                            print("✅ Tag names:", tag_names)
                        else:
                            print("❌ Tag lookup failed:", result_json)
                    tags_id = self.env['crm.tag'].search([('name','=',  tag_names[0])])
                    sales_person = self.env['res.users'].search([('name', '=', lead['user_id'][1])]) if lead['user_id'] else False
                    partner_id = self.env['res.partner'].search([('name','=', lead['partner_id'][1])], limit=1) if lead['partner_id'] else False
                    stage_id = self.env['crm.stage'].search([('name','=', lead['stage_id'][1])]) if lead['stage_id'] else False
                    team_id = self.env['crm.team'].search([('name','=', lead['team_id'][1])]) if lead['team_id'] else False
                    lang_id = self.env['res.lang'].search([('name','=', lead['lang_id'][1])]) if lead['lang_id'] else False
                    campaign_id = self.env['utm.campaign'].search([('name','=', lead['campaign_id'][1])]) if lead['campaign_id'] else False
                    medium_id = self.env['utm.medium'].search([('name','=', lead['medium_id'][1])]) if lead['medium_id'] else False
                    source_id = self.env['utm.source'].search([('name','=', lead['source_id'][1])]) if lead['source_id'] else False
                    lost_reason = self.env['crm.lost.reason'].search([('name', '=', lead['lost_reason'][1])]) if lead['lost_reason'] else False
                    new_lead = self.env['crm.lead'].with_context(is_old_message=True,
                                mail_create_nolog=True,
                                mail_create_nosubscribe=True,
                                mail_notify_force_send=False,
                                mail_auto_delete=False,
                                mail_notify_user_signature=False,
                                mail_channel_noautofollow=True,
                                mail_channel_autofollow=False,).create({
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
                        'tag_ids': [(6, 0, tags_id.ids)] if lead.get('tag_ids') else False,
                        'partner_name': lead['partner_name'],
                        'city': lead['city'],
                        'lang_id': lang_id.id if lead['lang_id'] else False,
                        'referred': lead['referred'],
                        'expected_revenue': lead['expected_revenue'],
                        'probability': lead['probability'],
                        'website': lead['website'],
                        'campaign_id': campaign_id.id if lead['campaign_id'] else False,
                        'medium_id': medium_id.id if lead['medium_id'] else False,
                        'source_id': source_id.id if lead['source_id'] else False,
                        'lost_reason_id': lost_reason.id if lead['lost_reason'] else False
                    })
            else:
                print("❌ Failed to fetch leads:", leads_result)
        else:
            print("❌ Login failed:", result)

    def migrate_mail_messages(self):
        url = "https://class.glsystem.ae"
        db = "Class_test1"
        username = "admin"
        password = "Mo@sU@135"
        rpc_url = f"{url}/web/dataset/call_kw"
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
        if 'result' in result and result['result'].get('uid'):
            leads = self.env['crm.lead'].search([])
            for lead in leads:
                data = {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "model": "mail.message",
                        "method": "search_read",
                        "args": [
                            [
                                ('model', '=', 'crm.lead'),
                                ('res_id', '=', int(lead.lead_old_id))
                            ],
                            ['id', 'subject', 'body', 'date', 'author_id', 'email_from',
                             'message_type', 'subtype_id', 'record_name', 'tracking_value_ids',
                             'body', 'is_internal']
                        ],
                        "kwargs": {
                            # "limit": 10,
                            "order": "date asc"
                        }
                    }
                }

                res = session.post(rpc_url, json=data)
                messages = res.json().get('result', [])
                for msg in messages:
                    new_res_id = lead.id
                    if new_res_id:
                        author_id = self.env['res.partner'].search([('name','=', msg['author_id'][1])], limit=1) if msg['author_id'] else False
                        subtype_id = self.env['mail.message.subtype'].search([('name','=', msg['subtype_id'][1]),
                                                                              ('res_model','=', 'crm.lead')]) if msg['subtype_id'] else False
                        new_msg = self.env['mail.message'].sudo().with_context(is_old_message=True,
                            mail_create_nolog=True,
                            mail_create_nosubscribe=True,
                            mail_notify_force_send=False,
                            mail_auto_delete=False,
                            mail_notify_user_signature=False,
                            mail_channel_noautofollow=True,
                            mail_channel_autofollow=False,).create({
                            'subject': msg['subject'],
                            'res_id': new_res_id,
                            'model': 'crm.lead',
                            'author_id': author_id.id if msg['author_id'] else False,
                            'body': msg['body'],
                            'message_type': 'comment',
                            'subtype_id': subtype_id.id if msg['subtype_id'] else False,
                            'date': msg['date'],
                            'email_from': msg['email_from'],
                            'record_name': msg['record_name'],
                           # 'is_internal': lead.get('is_internal', False)
                        })
                        tracking_ids = msg['tracking_value_ids']
                        tracking_payload = {
                            "jsonrpc": "2.0",
                            "method": "call",
                            "params": {
                                "model": "mail.tracking.value",
                                "method": "read",
                                "args": [
                                    tracking_ids,
                                    ['field', 'old_value_text', 'new_value_text',
                                     'old_value_integer', 'new_value_integer',
                                     'old_value_float', 'new_value_float',
                                     'old_value_char', 'new_value_char',
                                     'old_value_datetime', 'new_value_datetime']
                                ],
                                "kwargs": {
                                }
                            }
                        }
                        res = session.post(rpc_url, json=tracking_payload)
                        tracking_result = res.json()
                        for tracking in tracking_result['result']:
                            field_name = tracking['field'][1]
                            field_label = field_name.split(' (')[0]
                            field_id = self.env['ir.model.fields'].search([(
                                'field_description','=', field_label
                            ), ('model_id.model', '=', 'crm.lead')])
                            self.env['mail.tracking.value'].create({
                                'mail_message_id': new_msg.id,
                                'field_id': field_id.id,
                                'old_value_text': tracking['old_value_text'],
                                'new_value_text': tracking['new_value_text'],
                                'old_value_integer': tracking['old_value_integer'],
                                'new_value_integer': tracking['new_value_integer'],
                                'old_value_float': tracking['old_value_float'],
                                'new_value_float': tracking['new_value_float'],
                                'old_value_char': tracking['old_value_char'],
                                'new_value_char': tracking['new_value_char'],
                                'old_value_datetime': tracking['old_value_datetime'],
                                'new_value_datetime': tracking['new_value_datetime'],
                            })

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


#class MailMessage(models.Model):
 #   _inherit = 'mail.message'

  #  @api.model_create_multi
   # def create(self, vals_list):
    #    if self._context.get('is_old_message'):
     #       return super(MailMessage, self).create(vals_list)
        # If context doesn't allow creation, do not create
        # _logger.warning("Blocked mail.message create from: \n%s", ''.join(traceback.format_stack()))
      #  return self.browse([])  # Return an empty recordset safely
