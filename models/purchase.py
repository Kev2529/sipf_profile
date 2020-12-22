from odoo import api, exceptions, fields, models, _


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = 'purchase.order'

    project_id = fields.Many2one(
        comodel_name='project.project', string='Linked Project',
        help='Choose the Project this purchase order is linked to')
