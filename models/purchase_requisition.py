from odoo import api, exceptions, fields, models, _


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    def _get_my_department(self):
        employees = self.env.user.employee_ids
        return (employees[0].department_id if employees
                else self.env['hr.department'] or False)

    department_id = fields.Many2one(
        comodel_name='hr.department', string='Department',
        default=_get_my_department,
        help='Select the Department the purchase requisition is for')
    account_analytic_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account',
        compute='_compute_analytic_account',
        inverse='_inverse_analytic_account',
        help='This account will be propagated to all lines, if you need '
        'to use different accounts, define the account at line level.',
    )
    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag', string='Analytic Tags',
        inverse='_inverse_analytic_tags',
        help='This account will be propagated to all lines, if you need '
        'to use different accounts, define the account at line level.',
    )
    nomenclature_europe_id = fields.Many2one(
        comodel_name='nomenclature.europe', string='Nomenclature Europe',
        inverse='_inverse_nomenclature',
    )

    @api.onchange('user_id')
    def onchange_user_id(self):
        employees = self.user_id.employee_ids
        self.department_id = (employees[0].department_id if employees
                              else self.env['hr.department'] or False)

    @api.depends("line_ids.account_analytic_id")
    def _compute_analytic_account(self):
        for rec in self:
            account = rec.mapped("line_ids.account_analytic_id")
            if len(account) == 1:
                rec.account_analytic_id = account.id
            else:
                rec.account_analytic_id = False

    def _inverse_analytic_account(self):
        for rec in self:
            if rec.account_analytic_id:
                for line in rec.line_ids:
                    line.account_analytic_id = rec.account_analytic_id

    def _inverse_analytic_tags(self):
        for rec in self:
            if rec.analytic_tag_ids:
                for line in rec.line_ids:
                    line.analytic_tag_ids = rec.analytic_tag_ids

    def _inverse_nomenclature(self):
        for rec in self:
            if rec.nomenclature_europe_id:
                for line in rec.line_ids:
                    line.nomenclature_europe_id = rec.nomenclature_europe_id


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    nomenclature_europe_id = fields.Many2one(
        comodel_name='nomenclature.europe', string='Nomenclature Europe',)

    def _prepare_purchase_order_line(
            self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        res = super(PurchaseRequisitionLine, self)._prepare_purchase_order_line(
            name, product_qty=product_qty, price_unit=price_unit, taxes_ids=taxes_ids)
        nomenclature = self.nomenclature_europe_id
        if nomenclature:
            res['nomenclature_europe_id'] = nomenclature.id
        return res
