from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    project_id = fields.Many2one(
        comodel_name='project.project', string='BAF Procedure',
        domain="[('is_procedure_baf', '=', True), ('is_template', '=', False)]",
        help='Choose the BAF Procedure this purchase order is managed in')
    department_id = fields.Many2one(comodel_name='hr.department', string='Department', help='This is the Department the purchase order is for')
    account_budget_id = fields.Many2one(
        'account.account', string='Budgeted Account',
        compute='_compute_budget_account',
        inverse='_inverse_budget_account',
        index=True, ondelete="cascade",
        domain="[('deprecated', '=', False), ('company_id', '=', 'company_id'),('is_off_balance', '=', False)]",
        check_company=True,
        tracking=True)

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        super(PurchaseOrder, self)._onchange_requisition_id()
        self.department_id = self.requisition_id.department_id.id or False

    @api.depends("order_line.account_budget_id")
    def _compute_budget_account(self):
        for rec in self:
            account = rec.mapped("order_line.account_budget_id")
            if len(account) == 1:
                rec.account_budget_id = account.id
            else:
                rec.account_budget_id = False

    def _inverse_budget_account(self):
        for rec in self:
            if rec.account_budget_id:
                for line in rec.order_line:
                    line.account_budget_id = rec.account_budget_id

    def button_confirm(self):
        for order in self:
            if any(
                    not line.nomenclature_europe_id
                    for line in order.order_line
            ):
                raise ValidationError(_('Nomenclature is required on every line'))
            super(PurchaseOrder, self).button_confirm()
        return True


class PurchaseOrderLine(models.Model):
    _name = 'purchase.order.line'
    _inherit = 'purchase.order.line'

    nomenclature_europe_id = fields.Many2one(
        comodel_name='nomenclature.europe', string='Nomenclature SIPF',
        domain=[('nomenclature_sipf_id', '!=', False)],
    )
    account_budget_id = fields.Many2one(
        'account.account', string='Budgeted Account',
        index=True, ondelete="cascade",
        domain="[('deprecated', '=', False), ('company_id', '=', 'company_id'),('is_off_balance', '=', False)]",
        check_company=True)

    def _get_computed_account(self):
        self.ensure_one()
        self = self.with_company(self.order_id.company_id)

        if not self.product_id:
            return

        fiscal_position = self.order_id.fiscal_position_id
        accounts = self.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
        return accounts['expense'] or self.account_budget_id

    def _product_id_change(self):
        super(PurchaseOrderLine, self)._product_id_change()
        self.account_budget_id = self._get_computed_account()

    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move=move)
        nomenclature = self.nomenclature_europe_id
        account = self.account_budget_id
        if nomenclature:
            res.update({
                'nomenclature_europe_id': nomenclature,
                'account_budget_id': account,
            })
        if account:
            res.update({
                'account_budget_id': account,
            })
        return res
