# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class RejectApprovalWizard(models.TransientModel):
    _name = 'reject.approval.wizard'
    _description =' Reject Approval Wizard'

    rejection_reason_id = fields.Many2one('rejection.reason', string='Rejection Reason')
    comments = fields.Char(string='Comments')

    def reject(self):
        lead_id = self.env.context.get('active_id')
        lead = self.env['crm.lead'].browse(lead_id)
        lead.state = 'reject'
        msg = "Rejected : %s,\n%s" %(self.rejection_reason_id.name, self.comments)
        lead.message_post(body=msg)
        return {'type': 'ir.actions.act_window_close'}
