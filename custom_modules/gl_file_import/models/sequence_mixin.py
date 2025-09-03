# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64
import tempfile
import openpyxl
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from odoo.tools.misc import format_date

class SequenceMixin(models.AbstractModel):
    _inherit = 'sequence.mixin'

    @api.constrains(lambda self: (self._sequence_field, self._sequence_date_field))
    def _constrains_date_sequence(self):
        # Make it possible to bypass the constraint to allow edition of already messed up documents.
        # /!\ Do not use this to completely disable the constraint as it will make this mixin unreliable.
        constraint_date = fields.Date.to_date(self.env['ir.config_parameter'].sudo().get_param(
            'sequence.mixin.constraint_start_date',
            '1970-01-01'
        ))
        for record in self:
            if not record._must_check_constrains_date_sequence():
                continue
            date = fields.Date.to_date(record[record._sequence_date_field])
            sequence = record[record._sequence_field]
            if (
                    sequence
                    and date
                    and date > constraint_date
                    and not record._sequence_matches_date()
            ):
                pass
                # raise ValidationError(_(
                #     "The %(date_field)s (%(date)s) you've entered isn't aligned with the existing sequence number (%(sequence)s). Clear the sequence number to proceed.\n"
                #     "To maintain date-based sequences, select entries and use the resequence option from the actions menu, available in developer mode.",
                #     date_field=record._fields[record._sequence_date_field]._description_string(self.env),
                #     date=format_date(self.env, date),
                #     sequence=sequence,
                # ))
