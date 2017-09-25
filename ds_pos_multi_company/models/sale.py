from datetime import datetime, timedelta
from openerp import api, fields, models, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from openerp.exceptions import UserError

class SaleOrder(models.Model):
	_inherit = "sale.order"

	@api.model
	def _default_warehouse_id(self):
		res = super(SaleOrder,self)._default_warehouse_id()
		company_id = self.env.context.get('company_id') or self.env.user.company_id.id
		res = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1)
		return res
	
	

	warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse',
		required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
		default=_default_warehouse_id)

	@api.multi
	def _prepare_invoice(self):
		"""
		Prepare the dict of values to create the new invoice for a sales order. This method may be
		overridden to implement custom invoice generation (making sure to call super() to establish
		a clean extension chain).
		"""

		self.ensure_one()
		res = super(SaleOrder,self)._prepare_invoice()
		journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
		if not journal_id:
			raise UserError(_('Please define an accounting sale journal for this company.'))
		journal = self.env['account.journal'].search([('id','=',journal_id)])
		account_id = journal.default_credit_account_id and journal.default_credit_account_id.id or False
		print "==========================",journal,account_id
		# print "error",error
		invoice_vals = {
			'name': self.client_order_ref or '',
			'origin': self.name,
			'type': 'out_invoice',
			'account_id': account_id or self.partner_invoice_id.property_account_receivable_id.id,
			'partner_id': self.partner_invoice_id.id,
			'journal_id': journal_id,
			'currency_id': self.pricelist_id.currency_id.id,
			'comment': self.note,
			'payment_term_id': self.payment_term_id.id,
			'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
			'company_id': self.company_id.id,
			'user_id': self.user_id and self.user_id.id,
			'team_id': self.team_id.id
		}
		return invoice_vals

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	@api.multi
	def _prepare_order_line_procurement(self, group_id=False):
		vals = super(SaleOrderLine, self)._prepare_order_line_procurement(group_id=group_id)
		date_planned = datetime.strptime(self.order_id.date_order, DEFAULT_SERVER_DATETIME_FORMAT)\
			+ timedelta(days=self.customer_lead or 0.0) - timedelta(days=self.order_id.company_id.security_lead)
		
		company_id = self.company_id.id
		location_id = self.env['stock.location'].search([('usage','=','customer'),('company_id','=',company_id)])
		print "====================",location_id
		# print error
		vals.update({
			'date_planned': date_planned.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
			'location_id': location_id and location_id.id or self.order_id.partner_shipping_id.property_stock_customer.id,
			'route_ids': self.route_id and [(4, self.route_id.id)] or [],
			'warehouse_id': self.order_id.warehouse_id and self.order_id.warehouse_id.id or False,
			'partner_dest_id': self.order_id.partner_shipping_id.id,
			'sale_line_id': self.id,
		})
		return vals