# © 2016 Julien Coux (Camptocamp)
# © 2018 Forest and Biomass Romania SA
# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero


class TrialBalanceReport(models.AbstractModel):
    _inherit = "report.account_financial_report.trial_balance"

    def _get_initial_balances_bs_ml_domain(
        self,
        account_ids,
        journal_ids,
        master_company_ids,
        partner_ids,
        company_id,
        date_from,
        only_posted_moves,
        show_partner_details,
    ):
        accounts_domain = [
            ("company_ids", "in", [company_id]),
            ("include_initial_balance", "=", True),
        ]
        if account_ids:
            accounts_domain += [("id", "in", account_ids)]
        domain = [("date", "<", date_from)]
        accounts = self.env["account.account"].search(accounts_domain)
        domain += [("account_id", "in", accounts.ids)]
        if company_id:
            domain += [("company_id", "=", company_id)]
        if journal_ids:
            domain += [("journal_id", "in", journal_ids)]
        if master_company_ids:
            domain += [("move_id.master_company_id", "in", master_company_ids)]
        if partner_ids:
            domain += [("partner_id", "in", partner_ids)]
        if only_posted_moves:
            domain += [("move_id.state", "=", "posted")]
        else:
            domain += [("move_id.state", "in", ["posted", "draft"])]
        if show_partner_details:
            domain += [
                (
                    "account_id.account_type",
                    "in",
                    ["asset_receivable", "liability_payable"],
                )
            ]
        return domain


    def _get_initial_balances_pl_ml_domain(
        self,
        account_ids,
        journal_ids,
        master_company_ids,
        partner_ids,
        company_id,
        date_from,
        only_posted_moves,
        show_partner_details,
        fy_start_date,
    ):
        accounts_domain = [
            ("company_ids", "in", [company_id]),
            ("include_initial_balance", "=", False),
        ]
        if account_ids:
            accounts_domain += [("id", "in", account_ids)]
        domain = [("date", "<", date_from), ("date", ">=", fy_start_date)]
        accounts = self.env["account.account"].search(accounts_domain)
        domain += [("account_id", "in", accounts.ids)]
        if company_id:
            domain += [("company_id", "=", company_id)]
        if journal_ids:
            domain += [("journal_id", "in", journal_ids)]
        if master_company_ids:
            domain += [("move_id.master_company_id", "in", master_company_ids)]
        if partner_ids:
            domain += [("partner_id", "in", partner_ids)]
        if only_posted_moves:
            domain += [("move_id.state", "=", "posted")]
        else:
            domain += [("move_id.state", "in", ["posted", "draft"])]
        if show_partner_details:
            domain += [
                (
                    "account_id.account_type",
                    "in",
                    ["asset_receivable", "liability_payable"],
                )
            ]
        return domain

    @api.model
    def _get_period_ml_domain(
        self,
        account_ids,
        journal_ids,
        master_company_ids,
        partner_ids,
        company_id,
        date_to,
        date_from,
        only_posted_moves,
        show_partner_details,
    ):
        domain = [
            ("display_type", "not in", ["line_note", "line_section"]),
            ("date", ">=", date_from),
            ("date", "<=", date_to),
        ]
        if company_id:
            domain += [("company_id", "=", company_id)]
        if account_ids:
            domain += [("account_id", "in", account_ids)]
        if journal_ids:
            domain += [("journal_id", "in", journal_ids)]
        if master_company_ids:
            domain += [("move_id.master_company_id", "in", master_company_ids)]
        if partner_ids:
            domain += [("partner_id", "in", partner_ids)]
        if only_posted_moves:
            domain += [("move_id.state", "=", "posted")]
        else:
            domain += [("move_id.state", "in", ["posted", "draft"])]
        if show_partner_details:
            domain += [
                (
                    "account_id.account_type",
                    "in",
                    ["asset_receivable", "liability_payable"],
                )
            ]
        return domain

    def _get_initial_balance_fy_pl_ml_domain(
        self,
        account_ids,
        journal_ids,
        master_company_ids,
        partner_ids,
        company_id,
        fy_start_date,
        only_posted_moves,
        show_partner_details,
    ):
        accounts_domain = [
            ("company_ids", "in", [company_id]),
            ("include_initial_balance", "=", False),
        ]
        if account_ids:
            accounts_domain += [("id", "in", account_ids)]
        domain = [("date", "<", fy_start_date)]
        accounts = self.env["account.account"].search(accounts_domain)
        domain += [("account_id", "in", accounts.ids)]
        if company_id:
            domain += [("company_id", "=", company_id)]
        if journal_ids:
            domain += [("journal_id", "in", journal_ids)]
        if master_company_ids:
            domain += [("move_id.master_company_id", "in", master_company_ids)]
        if partner_ids:
            domain += [("partner_id", "in", partner_ids)]
        if only_posted_moves:
            domain += [("move_id.state", "=", "posted")]
        else:
            domain += [("move_id.state", "in", ["posted", "draft"])]
        if show_partner_details:
            domain += [
                (
                    "account_id.account_type",
                    "in",
                    ["asset_receivable", "liability_payable"],
                )
            ]
        return domain

    def _get_pl_initial_balance(
        self,
        account_ids,
        journal_ids,
        master_company_ids,
        partner_ids,
        company_id,
        fy_start_date,
        only_posted_moves,
        show_partner_details,
        foreign_currency,
    ):
        domain = self._get_initial_balance_fy_pl_ml_domain(
            account_ids,
            journal_ids,
            master_company_ids,
            partner_ids,
            company_id,
            fy_start_date,
            only_posted_moves,
            show_partner_details,
        )
        initial_balances = self.env["account.move.line"].read_group(
            domain=domain,
            fields=["account_id", "balance", "amount_currency:sum"],
            groupby=["account_id"],
        )
        pl_initial_balance = 0.0
        pl_initial_currency_balance = 0.0
        for initial_balance in initial_balances:
            pl_initial_balance += initial_balance["balance"]
            if foreign_currency:
                pl_initial_currency_balance += round(
                    initial_balance["amount_currency"], 2
                )
        return pl_initial_balance, pl_initial_currency_balance

    # flake8: noqa: C901
    @api.model
    def _get_data(
        self,
        account_ids,
        journal_ids,
        master_company_ids,
        partner_ids,
        company_id,
        date_to,
        date_from,
        foreign_currency,
        only_posted_moves,
        show_partner_details,
        hide_account_at_0,
        unaffected_earnings_account,
        fy_start_date,
        grouped_by,
    ):
        accounts_domain = [("company_ids", "in", [company_id])]
        if account_ids:
            accounts_domain += [("id", "in", account_ids)]
            # If explicit list of accounts is provided,
            # don't include unaffected earnings account
            unaffected_earnings_account = False
        accounts = self.env["account.account"].search(accounts_domain)
        tb_initial_acc = []
        for account in accounts:
            tb_initial_acc.append(
                {"account_id": account.id, "balance": 0.0, "amount_currency": 0.0}
            )
        groupby_fields = ["account_id"]
        if grouped_by:
            groupby_fields.append("analytic_account_ids")
        initial_domain_bs = self._get_initial_balances_bs_ml_domain(
            account_ids,
            journal_ids,
            master_company_ids,
            partner_ids,
            company_id,
            date_from,
            only_posted_moves,
            show_partner_details,
        )
        tb_initial_acc_bs = self.env["account.move.line"].read_group(
            domain=initial_domain_bs,
            fields=["account_id", "balance", "amount_currency:sum"],
            groupby=groupby_fields,
        )
        initial_domain_pl = self._get_initial_balances_pl_ml_domain(
            account_ids,
            journal_ids,
            master_company_ids,
            partner_ids,
            company_id,
            date_from,
            only_posted_moves,
            show_partner_details,
            fy_start_date,
        )
        tb_initial_acc_pl = self.env["account.move.line"].read_group(
            domain=initial_domain_pl,
            fields=["account_id", "balance", "amount_currency:sum"],
            groupby=groupby_fields,
        )
        tb_initial_acc_rg = tb_initial_acc_bs + tb_initial_acc_pl
        for account_rg in tb_initial_acc_rg:
            element = list(
                filter(
                    lambda acc_dict: acc_dict["account_id"]
                    == account_rg["account_id"][0],
                    tb_initial_acc,
                )
            )
            if element:
                element[0]["balance"] += account_rg["balance"]
                element[0]["amount_currency"] += account_rg["amount_currency"]
                if "__context" in account_rg and "group_by" in account_rg["__context"]:
                    group_by = account_rg["__context"]["group_by"][0]
                    gb_data = {}
                    account_rg_grouped = self.env["account.move.line"].read_group(
                        domain=account_rg["__domain"],
                        fields=[group_by, "balance", "amount_currency:sum"],
                        groupby=[group_by],
                    )
                    for a_rg2 in account_rg_grouped:
                        gb_id = a_rg2[group_by][0] if a_rg2[group_by] else 0
                        gb_data[gb_id] = {
                            "balance": a_rg2["balance"],
                            "amount_currency": a_rg2["amount_currency"],
                        }
                    element[0]["group_by"] = group_by
                    element[0]["group_by_data"] = gb_data
        if hide_account_at_0:
            tb_initial_acc = [p for p in tb_initial_acc if p["balance"] != 0]

        period_domain = self._get_period_ml_domain(
            account_ids,
            journal_ids,
            master_company_ids,
            partner_ids,
            company_id,
            date_to,
            date_from,
            only_posted_moves,
            show_partner_details,
        )
        tb_period_acc = self.env["account.move.line"].read_group(
            domain=period_domain,
            fields=["account_id", "debit", "credit", "balance", "amount_currency:sum"],
            groupby=groupby_fields,
        )

        if show_partner_details:
            tb_initial_prt_bs = self.env["account.move.line"].read_group(
                domain=initial_domain_bs,
                fields=["account_id", "partner_id", "balance", "amount_currency:sum"],
                groupby=["account_id", "partner_id"],
                lazy=False,
            )
            tb_initial_prt_pl = self.env["account.move.line"].read_group(
                domain=initial_domain_pl,
                fields=["account_id", "partner_id", "balance", "amount_currency:sum"],
                groupby=["account_id", "partner_id"],
            )
            tb_initial_prt = tb_initial_prt_bs + tb_initial_prt_pl
            if hide_account_at_0:
                tb_initial_prt = [p for p in tb_initial_prt if p["balance"] != 0]
            tb_period_prt = self.env["account.move.line"].read_group(
                domain=period_domain,
                fields=[
                    "account_id",
                    "partner_id",
                    "debit",
                    "credit",
                    "balance",
                    "amount_currency:sum",
                ],
                groupby=["account_id", "partner_id"],
                lazy=False,
            )
        total_amount = {}
        partners_data = []
        total_amount = self._compute_account_amount(
            total_amount, tb_initial_acc, tb_period_acc, foreign_currency
        )
        if show_partner_details:
            total_amount, partners_data = self._compute_partner_amount(
                total_amount, tb_initial_prt, tb_period_prt, foreign_currency
            )
        # Remove accounts a 0 from collections
        if hide_account_at_0:
            company = self.env["res.company"].browse(company_id)
            self._remove_accounts_at_cero(total_amount, show_partner_details, company)

        accounts_ids = list(total_amount.keys())
        unaffected_id = unaffected_earnings_account
        if unaffected_id:
            if unaffected_id not in accounts_ids:
                accounts_ids.append(unaffected_id)
                total_amount[unaffected_id] = {}
                total_amount[unaffected_id]["initial_balance"] = 0.0
                total_amount[unaffected_id]["balance"] = 0.0
                total_amount[unaffected_id]["credit"] = 0.0
                total_amount[unaffected_id]["debit"] = 0.0
                total_amount[unaffected_id]["ending_balance"] = 0.0
                if foreign_currency:
                    total_amount[unaffected_id]["amount_currency"] = 0
                    total_amount[unaffected_id]["initial_currency_balance"] = 0.0
                    total_amount[unaffected_id]["ending_currency_balance"] = 0.0
            if grouped_by:
                total_amount[unaffected_id]["group_by"] = grouped_by
                total_amount[unaffected_id]["group_by_data"] = {}
                # Fix to prevent side effects
                if (
                    foreign_currency
                    and "amount_currency" not in total_amount[unaffected_id]
                ):
                    total_amount[unaffected_id]["amount_currency"] = 0
                group_by_data_item = self._prepare_total_amount(
                    total_amount[unaffected_id], foreign_currency
                )
                total_amount[unaffected_id]["group_by_data"][0] = group_by_data_item
        accounts_data = self._get_accounts_data(accounts_ids)
        (
            pl_initial_balance,
            pl_initial_currency_balance,
        ) = self._get_pl_initial_balance(
            account_ids,
            journal_ids,
            master_company_ids,
            partner_ids,
            company_id,
            fy_start_date,
            only_posted_moves,
            show_partner_details,
            foreign_currency,
        )
        if unaffected_id:
            total_amount[unaffected_id]["ending_balance"] += pl_initial_balance
            total_amount[unaffected_id]["initial_balance"] += pl_initial_balance
            if foreign_currency:
                total_amount[unaffected_id]["ending_currency_balance"] += (
                    pl_initial_currency_balance
                )
                total_amount[unaffected_id]["initial_currency_balance"] += (
                    pl_initial_currency_balance
                )
            if grouped_by:
                total_amount[unaffected_id]["group_by_data"][0]["ending_balance"] = (
                    total_amount[unaffected_id]["ending_balance"]
                )
                total_amount[unaffected_id]["group_by_data"][0]["initial_balance"] = (
                    total_amount[unaffected_id]["initial_balance"]
                )
                if foreign_currency:
                    total_amount[unaffected_id]["group_by_data"][0][
                        "ending_currency_balance"
                    ] = total_amount[unaffected_id]["ending_currency_balance"]
                    total_amount[unaffected_id]["group_by_data"][0][
                        "initial_currency_balance"
                    ] = total_amount[unaffected_id]["initial_currency_balance"]
        return total_amount, accounts_data, partners_data

    def _get_report_values(self, docids, data):
        show_partner_details = data["show_partner_details"]
        wizard_id = data["wizard_id"]
        company = self.env["res.company"].browse(data["company_id"])
        company_id = data["company_id"]
        partner_ids = data["partner_ids"]
        journal_ids = data["journal_ids"]
        master_company_ids = data["master_company_ids"]
        account_ids = data["account_ids"]
        date_to = data["date_to"]
        date_from = data["date_from"]
        hide_account_at_0 = data["hide_account_at_0"]
        show_hierarchy = data["show_hierarchy"]
        show_hierarchy_level = data["show_hierarchy_level"]
        foreign_currency = data["foreign_currency"]
        only_posted_moves = data["only_posted_moves"]
        unaffected_earnings_account = data["unaffected_earnings_account"]
        fy_start_date = data["fy_start_date"]
        grouped_by = data["grouped_by"]
        total_amount, accounts_data, partners_data = self._get_data(
            account_ids,
            journal_ids,
            master_company_ids,
            partner_ids,
            company_id,
            date_to,
            date_from,
            foreign_currency,
            only_posted_moves,
            show_partner_details,
            hide_account_at_0,
            unaffected_earnings_account,
            fy_start_date,
            grouped_by,
        )
        trial_balance_grouped = False
        total_amount_grouped = False
        if grouped_by:
            trial_balance_grouped, total_amount_grouped = self._get_data_grouped(
                total_amount, accounts_data, foreign_currency
            )
        trial_balance = []
        if not show_partner_details:
            for account_id in accounts_data.keys():
                accounts_data[account_id].update(
                    {
                        "initial_balance": total_amount[account_id]["initial_balance"],
                        "credit": total_amount[account_id]["credit"],
                        "debit": total_amount[account_id]["debit"],
                        "balance": total_amount[account_id]["balance"],
                        "ending_balance": total_amount[account_id]["ending_balance"],
                        "group_by": (
                            total_amount[account_id]["group_by"]
                            if "group_by" in total_amount[account_id]
                            else False
                        ),
                        "group_by_data": (
                            total_amount[account_id]["group_by_data"]
                            if "group_by_data" in total_amount[account_id]
                            else False
                        ),
                        "type": "account_type",
                    }
                )
                if foreign_currency:
                    accounts_data[account_id].update(
                        {
                            "ending_currency_balance": total_amount[account_id][
                                "ending_currency_balance"
                            ],
                            "initial_currency_balance": total_amount[account_id][
                                "initial_currency_balance"
                            ],
                        }
                    )
            if show_hierarchy:
                groups_data = self._get_groups_data(
                    accounts_data, total_amount, foreign_currency
                )
                trial_balance = list(groups_data.values())
                trial_balance += list(accounts_data.values())
                trial_balance = sorted(trial_balance, key=lambda k: k["complete_code"])
                for trial in trial_balance:
                    counter = trial["complete_code"].count("/")
                    trial["level"] = counter
            else:
                trial_balance = list(accounts_data.values())
                trial_balance = sorted(trial_balance, key=lambda k: k["code"])
        else:
            if foreign_currency:
                for account_id in accounts_data.keys():
                    total_amount[account_id]["currency_id"] = accounts_data[account_id][
                        "currency_id"
                    ]
                    total_amount[account_id]["currency_name"] = accounts_data[
                        account_id
                    ]["currency_name"]
        return {
            "doc_ids": [wizard_id],
            "doc_model": "trial.balance.report.wizard",
            "docs": self.env["trial.balance.report.wizard"].browse(wizard_id),
            "foreign_currency": data["foreign_currency"],
            "company_name": company.display_name,
            "company_currency": company.currency_id,
            "currency_name": company.currency_id.name,
            "date_from": data["date_from"],
            "date_to": data["date_to"],
            "only_posted_moves": data["only_posted_moves"],
            "hide_account_at_0": data["hide_account_at_0"],
            "show_partner_details": data["show_partner_details"],
            "limit_hierarchy_level": data["limit_hierarchy_level"],
            "show_hierarchy": show_hierarchy,
            "hide_parent_hierarchy_level": data["hide_parent_hierarchy_level"],
            "trial_balance": trial_balance,
            "trial_balance_grouped": trial_balance_grouped,
            "total_amount": total_amount,
            "total_amount_grouped": total_amount_grouped,
            "accounts_data": accounts_data,
            "partners_data": partners_data,
            "show_hierarchy_level": show_hierarchy_level,
            "currency_model": self.env["res.currency"],
            "grouped_by": grouped_by,
        }
