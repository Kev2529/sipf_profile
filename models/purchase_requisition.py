from odoo import api, exceptions, fields, models, _


class PurchaseRequisition(models.Model):
    _name = 'purchase.requisition'
    _inherit = 'purchase.requisition'

    department_id = fields.Many2one(
        comodel_name='hr.department', string='Department',
        help='Select the Department the purchase requisition is for')
