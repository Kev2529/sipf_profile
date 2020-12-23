from odoo import api, exceptions, fields, models, _


class NomenclatureSipf(models.Model):
    _name = 'nomenclature.sipf'
    _description = 'Nomenclature interne au SIPF'

    name = fields.Char(string='Code', size=64, help='Nomenclature SIPF')
    nomenclature_europe_ids = fields.One2many(
        comodel_name='nomenclature.europe', inverse_name='nomenclature_sipf_id',
        string='European Nomenclature', help='The corresponding European Nomenclature')
