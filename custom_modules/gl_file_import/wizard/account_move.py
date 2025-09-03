# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64
import tempfile
import openpyxl
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from odoo.tools.misc import format_date


class JournalEntryImportWizard(models.TransientModel):
    _name = 'je.import.wizard'

    file = fields.Binary('File', required=True)
    filename = fields.Char('File Name')

    def action_process_file(self):
        if not self.file:
            raise UserError("Please upload an XLSX file.")

        file_data = base64.b64decode(self.file)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(file_data)
            tmp.seek(0)
            wb = openpyxl.load_workbook(tmp.name)
            sheet = wb.active

            for row in sheet.iter_rows(min_row=2, values_only=True):
                reference = row[0]
                raw_date = row[1]
                accounting_date = None

                if reference and raw_date:
                    # Handle string like '05/12/2025'
                    if isinstance(raw_date, str):
                        try:
                            accounting_date = datetime.strptime(raw_date.strip(), '%d/%m/%Y').date()
                        except ValueError:
                            raise UserError(f"Invalid date format: {raw_date}")
                    # If it's already a datetime/date
                    elif isinstance(raw_date, datetime):
                        accounting_date = raw_date.date()
                    elif isinstance(raw_date, (int, float)):  # Excel serial
                        accounting_date = (datetime(1899, 12, 30) + timedelta(days=raw_date)).date()

                    if not accounting_date:
                        continue

                    formatted_date = accounting_date.strftime('%d/%m/%Y')
                    print(f"Processing Reference: {reference}, Date: {formatted_date}")

                    existing_journal_id = self.env['account.move'].search([
                        ('ref', '=', reference),
                        ('move_type', '=', 'entry')
                    ])

                    if existing_journal_id:
                        print("==JOURNAL ENTRY===", existing_journal_id, existing_journal_id.ref, existing_journal_id.name)
                        print("==DATE", accounting_date)
                        existing_journal_id.posted_before = False
                        existing_journal_id.button_draft()
                        existing_journal_id.name = False  # Clear existing name
                        existing_journal_id.update({
                            'date': accounting_date})
                        # Ensure sequence regenerates
                        # Force sequence assignment before posting
                        print("=====STATE",existing_journal_id.state)
                        existing_journal_id._compute_name()
                        print("======", existing_journal_id.name, existing_journal_id.date)
                        existing_journal_id.action_post()

        return {'type': 'ir.actions.act_window_close'}
