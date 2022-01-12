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


class PurchaseOrderReport(models.AbstractModel):
    _name = 'report.sipf_profile.sipf_purchase_order'

    def _get_highest_parent(self, partner):
        if partner.parent_id:
            return self._get_highest_parent(partner.parent_id)
        else:
            return partner

    def _get_report_values(self, docids, data=None):
        docs = self.env['purchase.order'].browse(docids)
        company_id = docs.company_id.parent_id and docs.company_id.parent_id or docs.company_id
        no_parent_partner = self.env['hr.employee'].sudo().search([
            ('parent_id', '=', False),
            ('company_id', '=', company_id.id)
        ])
        data = {
            'docs': docs,
            'no_parent_partner': no_parent_partner[0]
        }

        if (docs.order_type in (
            self.env.ref('purchase_order_type.po_type_regular'),
            self.env.ref('sipf_profile.po_type_requisition'),
            self.env.ref('l10n_pf_purchase_freight.po_type_freight')
        ) and docs.requisition_id.type_id in (
                self.env.ref('sipf_profile.type_epac'),
                self.env.ref('sipf_profile.type_marche')
        )):
            epac_initial_id = self._get_highest_parent(docs.requisition_id)
            data['initial_code_visa'] = epac_initial_id.code_visa
        return data


class PurchaseRequisitionReport(models.AbstractModel):
    _name = 'report.sipf_profile.sipf_purchase_requisition_epac'

    def _get_highest_parent(self, partner):
        if partner.parent_id:
            return self._get_highest_parent(partner.parent_id)
        else:
            return partner

    def _get_report_values(self, docids, data=None):
        # get the records selected for this rendering of the report
        docs = self.env['purchase.requisition'].browse(docids)
        epac_initial_id = self._get_highest_parent(docs[0])
        epac_childs = self.env['purchase.requisition'].search([
            ('id', 'child_of', epac_initial_id.id),
            ('state', 'not in', ['draft'])
        ], order='create_date asc')
        counter = 0
        for i, child in enumerate(epac_childs):
            if (child == docs):
                counter = i
                break
        # get employee with no parent_id of company or parent company if exists
        company_id = docs.company_id.parent_id and docs.company_id.parent_id or docs.company_id
        no_parent_partner = self.env['hr.employee'].sudo().search([
            ('parent_id', '=', False),
            ('company_id', '=', company_id.id)
        ])
        return {
            'docs': docs,
            'epac_counter': counter,
            'initial_code_visa': epac_initial_id.code_visa,
            'no_parent_partner': no_parent_partner[0]
        }
