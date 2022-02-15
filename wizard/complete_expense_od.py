# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import pytz


class CompleteExpenseOd(models.TransientModel):
    _name = 'complete.expense.od'
    _description = 'Complete Expense Sheet OD Form Wizard'
    _check_company_auto = True

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
        required=True
    )
    hr_expense_sheet_id = fields.Many2one(
        'hr.expense.sheet',
        default=lambda self: self._default_hr_expense_sheet_id(),
    )
    compensation_analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='Imputations budgétaires des indemnités',
    )

    def action_od_lines(self):
        self.ensure_one()

        # Clear hr_expense_sheet_id
        self.hr_expense_sheet_id.expense_line_ids = [
            (2, line.id, 0) for line in self.hr_expense_sheet_id.expense_line_ids]
        self._create_expense_sheet_lines()

    def _create_expense_sheet_lines(self):
        expense_type = self.hr_expense_sheet_id.expense_type

        # Create one or multiple lines depending of the expense type
        qty = self.hr_expense_sheet_id.duration
        if expense_type == 'overseas':
            self._create_expense(
                self.env.ref('sipf_profile.overseas_compensation_od'), qty)
        elif expense_type == 'formation':
            self._create_expense(
                self.env.ref('sipf_profile.formation_compensation_od'), qty)
        elif expense_type == 'meal_allowance' or 'mission':
            timezone = pytz.timezone(self._context.get('tz')
                                     or self.env.user.tz or 'UTC')
            lunch_not_included = dinner_not_included = 0
            departure_depart_hour = self.hr_expense_sheet_id.departure_depart_date.astimezone(
                timezone).time().hour
            arrival_return_hour = self.hr_expense_sheet_id.arrival_return_date.astimezone(
                timezone).time().hour
            # We calculate the number of lunch, dinner, night(only for mission type) to be substracted of the maximum possible depending on the duration
            #
            # Lunch meal compensation rule: only if expense_type started before/at 11:00 and ended at/after 14:00 (transportation included)
            # - first AND last day
            if (departure_depart_hour > 11 and arrival_return_hour < 14):
                lunch_not_included = 2
            # - first OR last day
            elif (departure_depart_hour > 11 or arrival_return_hour < 14):
                lunch_not_included = 1
            # Dinner meal compensation rule: only if expense_type started before/at 18:00 and ended at/after 21:00 (transportation included)
            # - first AND last day
            if (departure_depart_hour > 18 and arrival_return_hour <= 21):
                dinner_not_included = 2
            # - first OR last day
            elif (departure_depart_hour > 18 or arrival_return_hour <= 21):
                dinner_not_included = 1

            self._create_expense(
                self.env.ref('sipf_profile.' + expense_type + '_lunch_od'), qty - lunch_not_included)
            self._create_expense(
                self.env.ref('sipf_profile.' + expense_type + '_dinner_od'), qty - dinner_not_included)

            if expense_type == 'mission':
                night_not_included = 0
                arrival_depart_hour = self.hr_expense_sheet_id.arrival_depart_date.astimezone(
                    timezone).time().hour
                # Night compensation rule: only if expense_type started before 00:00 and ended at/after 5:00 (transportation included)
                # - first AND last day
                if (arrival_depart_hour >= 0
                        and arrival_return_hour < 5):
                    night_not_included = 2
                # - first OR last day
                elif (arrival_depart_hour >= 0
                      or arrival_return_hour < 5):
                    night_not_included = 1

                self._create_expense(
                    self.env.ref('sipf_profile.' + expense_type + '_night_od'), qty - night_not_included)

    def _create_expense(self, product_id, qty):
        expense = self.env['hr.expense'].create({
            'name': product_id.name or data.name,
            'product_id': product_id.id or data.id,
            'unit_amount': product_id.price_compute('standard_price')[product_id.id],
            'analytic_tag_ids': self.compensation_analytic_tag_ids,
            'tax_ids': product_id.supplier_taxes_id.filtered(
                lambda tax: tax.company_id == self.company_id),
        })
        expense.product_uom_id = expense.product_id.uom_id
        expense.sheet_id = self.hr_expense_sheet_id
        account = expense.product_id.product_tmpl_id._get_product_accounts()[
            'expense']
        if account:
            expense.account_id = account
        if qty:
            expense.quantity = qty
