from odoo import api, exceptions, fields, models, _


class Project(models.Model):
    _name = 'project.project'
    _inherit = 'project.project'

    purchase_order_ids = fields.One2many(
        comodel_name='purchase.order', inverse_name='project_id',
        string='Linked Purchase Orders')
    po_count = fields.Integer(compute='_compute_orders_number', string='Numbers of Orders')
    type_id = fields.Many2one(copy=True)

    def _compute_orders_number(self):
        for project in self:
            project.po_count = len(project.purchase_order_ids)
