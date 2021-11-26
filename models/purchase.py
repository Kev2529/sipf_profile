from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    ref = fields.Char('Ref', copy=False)
    project_id = fields.Many2one(
        comodel_name='project.project', string='BAF Procedure',
        domain="[('is_procedure_baf', '=', True), ('is_template', '=', False)]",
        help='Choose the BAF Procedure this purchase order is managed in')
    department_id = fields.Many2one(comodel_name='hr.department', string='Department', help='This is the Department the purchase order is for')
    account_budget_id = fields.Many2one(
        'account.account', string='Budgeted Account',
        compute='_compute_budget_account',
        inverse='_inverse_budget_account',
        index=True, ondelete="cascade",
        domain="[('deprecated', '=', False), ('company_id', '=', 'company_id'),('is_off_balance', '=', False)]",
        check_company=True,
        tracking=True)
    requisition_id = fields.Many2one(required=True)
    invest = fields.Selection(
        selection=[
            ('invest', 'Investissement'),
            ('fonction', 'Fonctionnement'),
        ],
        default='invest',
        string='Investissement/Fonctionnement')
    transport_ref = fields.Char(
        string='Transport ref.',
        help='Saisir le numéro de référence du vol ou du bateau.')
    departure_place = fields.Char(
        string='Lieu de départ',
        help="Saisir le lieu de départ.")
    arrival_place = fields.Char(
        string="Lieux visités",
        help="Saisir les lieux visités.")

    # Requisition's purchase order type specific fields
    option_date = fields.Date(
        string="Date d'option",
        help="Saisir la date d'option du vol si existante.")
    passenger_ids = fields.Many2many(
        comodel_name='hr.employee',
        string='Passager(s)',
        help='Choisir le(s) passager(s)')
    departure_date = fields.Date(string='Date de départ')
    return_date = fields.Date(string='Date de retour')
    expense_sheet_id = fields.Many2one('hr.expense.sheet', 'Expense sheet')

    # Freight's purchase order type specific fields
    partner_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string='Délivré à',
        help='Saisir la personne ou entreprise recevant le(s) colis')

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        super(PurchaseOrder, self)._onchange_requisition_id()
        self.department_id = self.requisition_id.department_id.id or False
        self.invest = self.requisition_id.invest

    @api.onchange('departure_date', 'return_date')
    def _onchange_travel_date(self):
        if (self.departure_date and self.return_date
                and self.departure_date > self.return_date):
            raise ValidationError(
                _('The departure date must be earlier than the return date.'))

    @api.depends("order_line.account_budget_id")
    def _compute_budget_account(self):
        for rec in self:
            account = rec.mapped("order_line.account_budget_id")
            if len(account) == 1:
                rec.account_budget_id = account.id
            else:
                rec.account_budget_id = False

    def _inverse_budget_account(self):
        for rec in self:
            if rec.account_budget_id:
                for line in rec.order_line:
                    line.account_budget_id = rec.account_budget_id

    def button_confirm(self):
        for order in self:
            if any(
                    not line.nomenclature_europe_id
                    for line in order.order_line
            ):
                raise ValidationError(_('Nomenclature is required on every line'))
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # We always want double validation
            order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        res = super(PurchaseOrder, self).button_confirm()
        return res

    def button_print_report(self):
        self.ensure_one()

        return self.env.ref('sipf_profile.report_purchase_order').report_action(self)

    def button_approve(self):
        res = super(PurchaseOrder, self).button_approve()
        for order in self:
            if not order.ref:
                # We have a special sequence for Freight
                if order.order_type == self.env.ref('l10n_pf_purchase_freight.po_type_freight'):
                    seq_date = fields.Date.context_today(self)
                    order.ref = (
                        self.env['ir.sequence']
                        .next_by_code('purchase.order.sipf.et', sequence_date=seq_date)
                    )
                    break
                if order.order_type == self.env.ref('sipf_profile.po_type_requisition'):
                    seq_date = fields.Date.context_today(self)
                    order.ref = (
                        self.env['ir.sequence']
                        .next_by_code('purchase.order.sipf.req', sequence_date=seq_date)
                    )
                    break
                # For other types, we have a sequence for each department
                if order.department_id:
                    ref_sequence_list = {
                        'sipf_profile.sipf_baf': 'purchase.order.sipf.baf',
                        'sipf_profile.sipf_bssi': 'purchase.order.sipf.bssi',
                        'sipf_profile.sipf_cpau': 'purchase.order.sipf.cpau',
                        'sipf_profile.sipf_dpo': 'purchase.order.sipf.dpo',
                        'sipf_profile.sipf_infra': 'purchase.order.sipf.infra',
                        'sipf_profile.sipf_projects': 'purchase.order.sipf.projects',
                        'sipf_profile.sipf_silog': 'purchase.order.sipf.silog'
                    }
                    if ref_sequence_list != {}:
                        for ref, seq in ref_sequence_list.items():
                            # Set the sequence number regarding the department
                            if self.env.ref(ref).id == order.department_id.id:
                                seq_date = fields.Date.context_today(self)
                                order.ref = (
                                    self.env['ir.sequence']
                                    .next_by_code(seq, sequence_date=seq_date)
                                )
                                break
                else:
                    raise UserError(
                        _('The department must be filled.'))

        return res


class PurchaseOrderLine(models.Model):
    _name = 'purchase.order.line'
    _inherit = 'purchase.order.line'

    nomenclature_europe_id = fields.Many2one(
        comodel_name='nomenclature.europe', string='Nomenclature SIPF',
        domain=[('nomenclature_sipf_id', '!=', False)],
    )
    account_budget_id = fields.Many2one(
        'account.account', string='Budgeted Account',
        index=True, ondelete="cascade",
        domain="[('deprecated', '=', False), ('company_id', '=', 'company_id'),('is_off_balance', '=', False)]",
        check_company=True)
    pack_qty = fields.Float(
        string='Pack Qty',
        digits='Pack Unit of Measure',
        required=True,
        default=1.0)

    def _get_computed_account(self):
        self.ensure_one()
        self = self.with_company(self.order_id.company_id)

        if not self.product_id:
            return

        fiscal_position = self.order_id.fiscal_position_id
        accounts = self.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
        return accounts['expense'] or self.account_budget_id

    def _product_id_change(self):
        super(PurchaseOrderLine, self)._product_id_change()
        self.account_budget_id = self._get_computed_account()

    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move=move)
        nomenclature = self.nomenclature_europe_id
        account = self.account_budget_id
        if nomenclature:
            res.update({
                'nomenclature_europe_id': nomenclature,
                'account_budget_id': account,
            })
        if account:
            res.update({
                'account_budget_id': account,
            })
        return res
