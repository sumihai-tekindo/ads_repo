from openerp.osv import fields,osv

class account_invoice(osv.osv):
	_inherit="account.invoice"


class account_invoice_line(osv.osv):
	_inherit="account.invoice.line"

