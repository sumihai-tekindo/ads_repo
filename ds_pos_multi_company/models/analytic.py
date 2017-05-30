from openerp import api, fields, models, _

class account_analytic_account(models.Model):
	_inherit = 'account.analytic.account'

	sale_type = fields.Selection([('retail','Retail'),('wholesale','Wholesale')],"Sale Type")
	online_type = fields.Selection([('online','Online'),('offline','Offline')],"Online Type")