from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    signature_delegation_threshold = fields.Monetary(
        string='Signature delegation threshold')
