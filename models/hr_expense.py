from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, time
import pytz


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    ref = fields.Char('Reference', readonly=True, copy=True)
    approve_date = fields.Date('Date approve', readonly=True, copy=True)
    expense_type = fields.Selection(
        selection_add=[
            ('mission', 'Mission'),
            ('formation', 'Formation'),
            ('meal_allowance', 'Panier'),
            ('overseas', 'Étranger'),
        ], ondelete={
            'mission': 'cascade',
            'formation': 'cascade',
            'meal_allowance': 'cascade',
            'overseas': 'cascade',
        })
    reglementary_text = fields.Char('Reglementary Text')
    bank_account_id = fields.Many2one(related='employee_id.bank_account_id')
    destination = fields.Char('Destination')
    mission_objective = fields.Char('Mission Objective')
    requisition_id = fields.Many2one(
        'purchase.requisition', string="Demande d'achat", copy=False)
    transportation = fields.Selection([
        ('aerial', 'Aerien'),
        ('maritime', 'Maritime'),
        ('land', 'Terrestre')
    ], default='aerial')
    departure_depart_date = fields.Datetime(
        string='Départ du voyage de départ')
    arrival_depart_date = fields.Datetime(
        string='Arrivée du voyage de départ')
    departure_return_date = fields.Datetime(
        string="Départ du voyage de retour")
    arrival_return_date = fields.Datetime(
        string="Arrivée du voyage de retour")
    duration = fields.Integer(
        compute='_compute_duration', string='Duration')
    transport_cost = fields.Monetary(
        string='Coût du transport', help='Cost of the transportation aerial/maritime/etc')
    transport_analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='Imputations budgétaires du transport',
    )
    transport_account_budget = fields.Char(
        'Article budgétaire du transport')

    def write(self, vals):
        if 'state' in vals and vals['state'] == 'approve':
            vals['ref'] = self.env['ir.sequence'].with_company(
                self.company_id).next_by_code('hr.expense.sheet')
            vals['approve_date'] = fields.Date.context_today(self)
        res = super(HrExpenseSheet, self).write(vals)
        return res

    @api.onchange('departure_depart_date', 'arrival_return_date')
    def _compute_duration(self):
        if self.departure_depart_date and self.arrival_return_date:
            if self.departure_depart_date > self.arrival_return_date:
                raise ValidationError(
                    _('The arrival return date must be after the departure depart date!'))
            timezone = pytz.timezone(self._context.get('tz')
                                     or self.env.user.tz or 'UTC')
            return_time = datetime.combine(
                self.arrival_return_date.astimezone(timezone), time(23, 59, 59))
            depart_time = datetime.combine(
                self.departure_depart_date.astimezone(timezone), time(0, 0, 0))
            self.duration = (return_time - depart_time).days + 1
        else:
            self.duration = 0

    @api.onchange('departure_depart_date', 'arrival_return_date')
    def onchange_travel_date(self):
        if self.expense_type == 'meal_allowance':
            self.arrival_depart_date = self.departure_depart_date
            self.departure_return_date = self.arrival_return_date

    def action_add_expense_line_wizard(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'sipf_profile.complete_expense_od_view')
        ctx = dict(self._context,
                   default_hr_expense_sheet_id=self.id,
                   default_compensation_analytic_tag_ids=self.transport_analytic_tag_ids.ids,
                   default_company_id=self.env.company.id,
                   active_ids=self.ids)
        ctx.pop('active_id', None)
        ctx['active_ids'] = self.ids
        ctx['active_model'] = 'hr.expense.sheet'
        action['context'] = ctx
        action['name'] = 'Ajouter automatiquement les compensations'
        return action
