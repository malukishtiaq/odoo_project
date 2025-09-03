# -*- coding: utf-8 -*-
from email.policy import default

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.fields import Command


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_internal_transfer = fields.Boolean(string='Internal Transfer')
    destination_journal_id = fields.Many2one(
        'account.journal',
        string="Destination Journal",
        domain=[('type', 'in', ['bank', 'cash'])]
    )

    def action_post(self):
        for payment in self:
            if payment.is_internal_transfer:
                if not payment.destination_journal_id:
                    raise ValidationError("Please select a Destination Journal.")

                if payment.move_id:
                    move = payment.move_id
                    if move.state != 'draft':
                        move.button_draft()
                    move.line_ids.unlink()
                else:
                    move = self.env['account.move'].create({
                        'journal_id': payment.journal_id.id,
                        'move_type': 'entry',
                        'date': payment.date,
                        'ref': payment.memo or 'Internal Transfer',
                    })
                    payment.move_id = move

                # Check if both journals are of type 'cash'
                if payment.journal_id.type == 'cash' and payment.destination_journal_id.type == 'cash':
                    # Direct cash-to-cash transfer
                    move.write({
                        'line_ids': [
                            (0, 0, {
                                'account_id': payment.journal_id.default_account_id.id,
                                'credit': payment.amount,
                                'debit': 0.0,
                                'partner_id': payment.partner_id.id,
                                'name': 'Cash Transfer Out',
                                'payment_id': payment.id,
                            }),
                            (0, 0, {
                                'account_id': payment.destination_journal_id.default_account_id.id,
                                'credit': 0.0,
                                'debit': payment.amount,
                                'partner_id': payment.partner_id.id,
                                'name': 'Cash Transfer In',
                            }),
                        ]
                    })
                else:
                    # Clearing account required
                    internal_account = self.env['account.account'].search([
                        ('is_internal_transfer_account', '=', True)
                    ], limit=1)

                    if not internal_account:
                        raise ValidationError("Please configure a 'Liquidity Transfer' account.")

                    move.write({
                        'line_ids': [
                            (0, 0, {
                                'account_id': payment.journal_id.default_account_id.id,
                                'credit': payment.amount,
                                'debit': 0.0,
                                'partner_id': payment.partner_id.id,
                                'name': 'Transfer Out',
                                'payment_id': payment.id,
                            }),
                            (0, 0, {
                                'account_id': internal_account.id,
                                'credit': 0.0,
                                'debit': payment.amount,
                                'name': 'To clearing',
                            }),
                            (0, 0, {
                                'account_id': internal_account.id,
                                'credit': payment.amount,
                                'debit': 0.0,
                                'name': 'From clearing',
                            }),
                            (0, 0, {
                                'account_id': payment.destination_journal_id.default_account_id.id,
                                'credit': 0.0,
                                'debit': payment.amount,
                                'partner_id': payment.partner_id.id,
                                'name': 'Transfer In',
                            }),
                        ]
                    })

                move.action_post()
                payment.state = 'paid'

            else:
                super(AccountPayment, payment).action_post()

    def _synchronize_to_moves(self, changed_fields):
        '''
            Update the account.move regarding the modified account.payment.
            :param changed_fields: A list containing all modified fields on account.payment.
        '''
        if self.is_internal_transfer:
            return
        if not any(field_name in changed_fields for field_name in self._get_trigger_fields_to_synchronize()):
            return

        for pay in self:
            liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()
            # Make sure to preserve the write-off amount.
            # This allows to create a new payment with custom 'line_ids'.
            write_off_line_vals = []
            if liquidity_lines and counterpart_lines and writeoff_lines:
                write_off_line_vals.append({
                    'name': writeoff_lines[0].name,
                    'account_id': writeoff_lines[0].account_id.id,
                    'partner_id': writeoff_lines[0].partner_id.id,
                    'currency_id': writeoff_lines[0].currency_id.id,
                    'amount_currency': sum(writeoff_lines.mapped('amount_currency')),
                    'balance': sum(writeoff_lines.mapped('balance')),
                })
            line_vals_list = pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)
            line_ids_commands = [
                Command.update(liquidity_lines.id, line_vals_list[0]) if liquidity_lines else Command.create(
                    line_vals_list[0]),
                Command.update(counterpart_lines.id, line_vals_list[1]) if counterpart_lines else Command.create(
                    line_vals_list[1])
            ]
            for line in writeoff_lines:
                line_ids_commands.append((2, line.id))
            for extra_line_vals in line_vals_list[2:]:
                line_ids_commands.append((0, 0, extra_line_vals))
            # Update the existing journal items.
            # If dealing with multiple write-off lines, they are dropped and a new one is generated.
            pay.move_id \
                .with_context(skip_invoice_sync=True) \
                .write({
                'partner_id': pay.partner_id.id,
                'currency_id': pay.currency_id.id,
                'partner_bank_id': pay.partner_bank_id.id,
                'line_ids': line_ids_commands,
            })


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_internal_transfer_account = fields.Boolean(string="Is Internal Transfer Account", default=False)