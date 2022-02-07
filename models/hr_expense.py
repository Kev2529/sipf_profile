from odoo import fields, models


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    ref = fields.Char('Reference', readonly=True, copy=True)
    approve_date = fields.Date('Date approve', readonly=True, copy=True)
    expense_type = fields.Selection(
        selection_add=[
            ('mission', 'Mission'),
            ('formation', 'Formation'),
            ('meal_allowance', 'Panier'),
            ('overseas', 'Étranger'),
        ], ondelete={
            'mission': 'cascade',
            'formation': 'cascade',
            'meal_allowance': 'cascade',
            'overseas': 'cascade',
        }, required=True, default='mission')

    def write(self, vals):
        if 'state' in vals and vals['state'] == 'approve':
            vals['ref'] = self.env['ir.sequence'].with_company(
                self.company_id).next_by_code('hr.expense.sheet')
            vals['approve_date'] = fields.Date.context_today(self)
        res = super(HrExpenseSheet, self).write(vals)
        return res
