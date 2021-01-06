
from odoo import api, fields, models, _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.depends('group_id')
    def _compute_is_project(self):
        group_project = self.env.ref('sipf_profile.analytic_group_projects')
        for account in self:
            if account.group_id == group_project:
                account.is_project = True
            else:
                account.is_project = False

    is_project = fields.Boolean(string='Is a Project',
                                store=True,
                                compute='_compute_is_project')
