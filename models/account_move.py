from odoo import api, exceptions, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    nomenclature_europe_id = fields.Many2one(
        comodel_name='nomenclature.europe', string='Nomenclature Europe',
        domain=[('nomenclature_sipf_id', '!=', False)],
    )
    account_budget_id = fields.Many2one(
        'account.account', string='Budgeted Account',
        index=True, ondelete="cascade",
        domain="[('deprecated', '=', False), ('company_id', '=', 'company_id'),('is_off_balance', '=', False)]",
        readonly=True,
        check_company=True,
        tracking=True)
