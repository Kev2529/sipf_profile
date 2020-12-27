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

    @api.onchange('user_id')
    def onchange_user_id(self):
        employees = self.user_id.employee_ids
        self.department_id = (employees[0].department_id if employees
                              else self.env['hr.department'] or False)


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
