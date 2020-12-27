from odoo import api, exceptions, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    project_id = fields.Many2one(
        comodel_name='project.project', string='Linked Project',
        help='Choose the Project this purchase order is linked to')
    department_id = fields.Many2one(comodel_name='hr.department', string='Department', help='This is the Department the purchase order is for')

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        super(PurchaseOrder, self)._onchange_requisition_id()
        self.department_id = self.requisition_id.department_id.id or False


class PurchaseOrderLine(models.Model):
    _name = 'purchase.order.line'
    _inherit = 'purchase.order.line'

    nomenclature_europe_id = fields.Many2one(
        comodel_name='nomenclature.europe', string='Nomenclature Europe',)

    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move=move)
        nomenclature = self.nomenclature_europe_id
        if nomenclature:
            res.update({
                'nomenclature_europe_id': nomenclature,
            })
        return res
