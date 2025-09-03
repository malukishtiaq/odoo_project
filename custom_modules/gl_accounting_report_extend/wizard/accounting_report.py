
from odoo import fields, api, models, _
from odoo.tools.misc import get_lang


class AccountingReport(models.TransientModel):
    _inherit = 'accounting.report'

    master_company_ids = fields.Many2many("master.company", string="Master Company")

    def _build_contexts(self, data):
        result = super(AccountingReport, self)._build_contexts(data)
        result['master_company_ids'] = 'master_company_ids' in data['form'] and data['form'][
            'master_company_ids'] or []
        return result

    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id', 'master_company_ids'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)
        return self.with_context(discard_logo_check=True)._print_report(data)


    # def _build_contexts(self, data):
    #     result = super()._build_contexts(data)
    #     result['master_company_ids'] = 'master_company_ids' in data['form'] and data['form'][
    #         'master_company_ids'] or []
    #     return result
    #
    # def view_report_pdf(self):
    #     """This function will be executed when we click the view button
    #     from the wizard. Based on the values provided in the wizard, this
    #     function will print pdf report"""
    #     self.ensure_one()
    #     data = dict()
    #     data['ids'] = self.env.context.get('active_ids', [])
    #     data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
    #     data['form'] = self.read(
    #         ['date_from', 'enable_filter', 'debit_credit', 'date_to',
    #          'account_report_id', 'target_move', 'view_format',
    #          'company_id', 'master_company_ids'])[0]
    #     used_context = self._build_contexts(data)
    #     data['form']['used_context'] = dict(
    #         used_context,
    #         lang=self.env.context.get('lang') or 'en_US')
    #
    #     report_lines = self.get_account_lines(data['form'])
    #     # find the journal items of these accounts
    #     journal_items = self.find_journal_items(report_lines, data['form'])
    #
    #     def set_report_level(rec):
    #         """This function is used to set the level of each item.
    #         This level will be used to set the alignment in the dynamic reports."""
    #         level = 1
    #         if not rec['parent']:
    #             return level
    #         else:
    #             for line in report_lines:
    #                 key = 'a_id' if line['type'] == 'account' else 'id'
    #                 if line[key] == rec['parent']:
    #                     return level + set_report_level(line)
    #
    #     # finding the root
    #     for item in report_lines:
    #         item['balance'] = round(item['balance'], 2)
    #         if not item['parent']:
    #             item['level'] = 1
    #             parent = item
    #             report_name = item['name']
    #             id = item['id']
    #             report_id = item['r_id']
    #         else:
    #             item['level'] = set_report_level(item)
    #     currency = self._get_currency()
    #     data['currency'] = currency
    #     data['journal_items'] = journal_items
    #     data['report_lines'] = report_lines
    #     # checking view type
    #     return self.env.ref(
    #         'base_accounting_kit.financial_report_pdf').report_action(self,
    #                                                                   data)
