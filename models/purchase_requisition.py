from odoo import api, exceptions, fields, models, _


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    department_id = fields.Many2one(
        comodel_name='hr.department', string='Department',
        help='Select the Department the purchase requisition is for')


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
