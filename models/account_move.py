from odoo import api, exceptions, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    nomenclature_europe_id = fields.Many2one(
        comodel_name='nomenclature.europe', string='Nomenclature Europe',)
