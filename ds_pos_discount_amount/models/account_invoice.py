import json
from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp import api, fields, models, _
from openerp.tools import float_is_zero, float_compare
from openerp.tools.misc import formatLang

from openerp.exceptions import UserError, RedirectWarning, ValidationError

import openerp.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
	_inherit = "account.invoice"

	@api.multi
	def get_taxes_values(self):
		res = super(AccountInvoice,self).get_taxes_values()
		tax_grouped = {}
		for line in self.invoice_line_ids:
			if line.invoice_id.type in ('out_invoice','out_refund'):
				if line.quantity==0 or line.quantity==0.0:
					price_unit=0.0
				else:
					price_unit = (line.price_unit * (1 - (line.discount or 0.0) / 100.0))-(line.discount_amount/line.quantity)
			else:
				price_unit = (line.price_unit * (1 - (line.discount or 0.0) / 100.0))
			taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']
			for tax in taxes:
				val = self._prepare_tax_line_vals(line, tax)
				key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

				if key not in tax_grouped:
					tax_grouped[key] = val
				else:
					tax_grouped[key]['amount'] += val['amount']
					tax_grouped[key]['base'] += val['base']
		return tax_grouped

class AccountInvoiceLine(models.Model):
	_inherit = "account.invoice.line"

	@api.one
	@api.depends('price_unit', 'discount','discount_amount', 'invoice_line_tax_ids', 'quantity',
		'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id')
	def _compute_price(self):
		currency = self.invoice_id and self.invoice_id.currency_id or None
		if self.invoice_id.type in ('out_invoice','out_refund'):
			if self.quantity==0 or self.quantity==0.0:
				price=0.0
			else:
				price = (self.price_unit * (1 - (self.discount or 0.0) / 100.0))-(self.discount_amount/self.quantity)
		else:
			price = (self.price_unit * (1 - (self.discount or 0.0) / 100.0))
		taxes = False
		if self.invoice_line_tax_ids:
			taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
		self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
		if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
			price_subtotal_signed = self.invoice_id.currency_id.compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
		sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
		self.price_subtotal_signed = price_subtotal_signed * sign


	discount_amount = fields.Float(string='Disc.Amt 2nd Lvl', required=False,default=0.0, digits=dp.get_precision('Product Price'))

