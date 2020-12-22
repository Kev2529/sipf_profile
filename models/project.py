from odoo import api, exceptions, fields, models, _


class Project(models.Model):
    _name = 'project.project'
    _inherit = 'project.project'

    purchase_order_id = fields.Many2one(
        comodel_name='purchase.order', string='Linked Purchase Order',
        help='Choose the Purchase Order this project is linked to')
