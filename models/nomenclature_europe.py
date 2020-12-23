from odoo import api, exceptions, fields, models, _
from odoo.osv import expression


class NomenclatureEurope(models.Model):
    _name = 'nomenclature.europe'
    _description = 'European Nomenclature'

    name = fields.Char(string='Code', size=64,
                       help='Code for European Nomenclature')
    nomenclature_sipf_id = fields.Many2one(
        comodel_name='nomenclature.sipf', string='SIPF Nomenclature',
        help='SIPF Nomenclature')

    def name_get(self):
        res = []
        for nomenclature in self:
            name = "%s (%s)" % (nomenclature.nomenclature_sipf_id.name,
                                nomenclature.name)
            res.append((nomenclature.id, name))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            args = args or []
            domain = [('nomenclature_sipf_id', operator, name)]
            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return super(NomenclatureEurope, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
