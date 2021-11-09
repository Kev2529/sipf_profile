# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    nomenclature_europe_id = fields.Many2one(
        comodel_name='nomenclature.europe',
        string='Nomenclature Europe',)
    nomenclature_sipf_id = fields.Many2one(
        comodel_name='nomenclature.sipf',
        string='Nomenclature SIPF',)

    def _select(self):
        return super(PurchaseReport, self)._select() + """,
    l.nomenclature_europe_id,
    n.nomenclature_sipf_id
        """

    def _from(self):
        return super(PurchaseReport, self)._from() + """
    LEFT JOIN nomenclature_europe n ON (l.nomenclature_europe_id=n.id)
        """

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + """,
    l.nomenclature_europe_id,
    n.nomenclature_sipf_id
        """


class PurchaseRequisitionReport(models.AbstractModel):
    _name = 'report.sipf_profile.sipf_purchase_requisition_epac'

    def _get_report_values(self, docids, data=None):
        # get the records selected for this rendering of the report
        docs = self.env['purchase.requisition'].browse(docids)

        sschap = ct = ''
        for tag in docs.analytic_tag_ids:
            if tag.analytic_distribution_ids.account_id.group_id == self.env.ref('sipf_profile.analytic_group_ct'):
                ct = tag.analytic_distribution_ids.account_id.code or tag.analytic_distribution_ids.name
            elif tag.analytic_distribution_ids.account_id.group_id == self.env.ref('sipf_profile.analytic_group_sschap'):
                sschap = tag.analytic_distribution_ids.account_id.code or tag.analytic_distribution_ids.name
        return {
            'docs': docs,
            'SSCHAP': sschap or '',
            'CT': ct or ''
        }
