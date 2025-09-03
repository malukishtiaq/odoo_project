
from odoo import api, fields, models, _
from odoo.tools.misc import get_lang


class TrialBalanceReport(models.TransientModel):
    _inherit = 'trial.balance.report.wizard'

    master_company_ids = fields.Many2many("master.company", string="Master Company")

    def _prepare_report_trial_balance(self):
        res = super(TrialBalanceReport, self)._prepare_report_trial_balance()
        res["master_company_ids"] = self.master_company_ids.ids or []
        return res