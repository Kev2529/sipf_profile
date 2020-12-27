# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    nomenclature_europe_id = fields.Many2one(
        comodel_name='nomenclature.europe',
        string='Nomenclature Europe',)
    nomenclature_sipf_id = fields.Many2one(
        comodel_name='nomenclature.sipf',
        string='Nomenclature SIPF',)

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + """,
    line.nomenclature_europe_id,
    n.nomenclature_sipf_id
        """

    def _from(self):
        return super(AccountInvoiceReport, self)._from() + """
    LEFT JOIN nomenclature_europe n ON (line.nomenclature_europe_id=n.id)
        """
