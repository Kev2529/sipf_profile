from odoo import api, exceptions, fields, models, _
from odoo.osv import expression


class NomenclatureSipf(models.Model):
    _name = 'nomenclature.sipf'
    _description = 'Nomenclature interne au SIPF'

    name = fields.Char(string='Code', size=64, help='Code Nomenclature SIPF')
    description = fields.Char(string='Description', help='Description Nomenclature SIPF')
    nomenclature_europe_ids = fields.One2many(
        comodel_name='nomenclature.europe', inverse_name='nomenclature_sipf_id',
        string='European Nomenclature', help='The corresponding European Nomenclature')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)

    _sql_constraints = [
        ('code_company_uniq', 'unique (name,company_id)', 'The code of the nomenclature must be unique per company !')
    ]

    def name_get(self):
        res = []
        for nomenclature in self:
            name = "%s-%s" % (nomenclature.name, nomenclature.description)
            res.append((nomenclature.id, name))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            args = args or []
            domain = ['|',
                      ('description', operator, name),
                      ('name', operator, name),
                      ]
            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return super(NomenclatureSipf, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
