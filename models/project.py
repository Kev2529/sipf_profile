from odoo import api, exceptions, fields, models, _


class Project(models.Model):
    _name = 'project.project'
    _inherit = 'project.project'

    purchase_order_ids = fields.One2many(
        comodel_name='purchase.order', inverse_name='project_id',
        string='Linked Purchase Orders')
    po_count = fields.Integer(compute='_compute_orders_number', string='Numbers of Orders')
    type_id = fields.Many2one(copy=True)
    is_procedure_baf = fields.Boolean(string='Is a BAF Procedure',
                                      store=True,
                                      compute='_compute_is_procedure_baf')

    def _compute_orders_number(self):
        for project in self:
            project.po_count = len(project.purchase_order_ids)

    @api.depends('type_id')
    def _compute_is_procedure_baf(self):
        type_project = self.env.ref('sipf_profile.project_type_procedure_baf')
        for project in self:
            if project.type_id == type_project:
                project.is_procedure_baf = True
            else:
                project.is_procedure_baf = False
