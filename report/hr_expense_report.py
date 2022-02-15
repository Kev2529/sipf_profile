# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools


class HrExpenseSheetReport(models.AbstractModel):
    _name = 'report.sipf_profile.sipf_hr_expense_sheet_od'

    def _get_highest_parent(self, partner):
        if partner.parent_id:
            return self._get_highest_parent(partner.parent_id)
        else:
            return partner

    def _get_highest_company(self, company):
        if company.parent_id:
            return self._get_highest_company(company.parent_id)
        else:
            return company

    def _get_report_values(self, docids, data=None):
        # get the records selected for this rendering of the report
        docs = self.env['hr.expense.sheet'].browse(docids)

        # get employee with no parent_id of company or parent company if exists
        if docs.expense_type == 'overseas':
            company_id = self._get_highest_company(docs.company_id)
        else:
            company_id = docs.company_id.parent_id and docs.company_id.parent_id or docs.company_id
        no_parent_partner = self.env['hr.employee'].sudo().search([
            ('parent_id', '=', False),
            ('company_id', '=', company_id.id)
        ])
        data = {
            'docs': docs,
            'no_parent_partner': no_parent_partner[0],
        }
        data['initial_code_visa'] = self._get_highest_parent(
            docs.requisition_id).code_visa

        return data
