from odoo import api, exceptions, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    nomenclature_europe_id = fields.Many2one(
        comodel_name='nomenclature.europe', string='Nomenclature SIPF',
        domain=[('nomenclature_sipf_id', '!=', False)],
    )
