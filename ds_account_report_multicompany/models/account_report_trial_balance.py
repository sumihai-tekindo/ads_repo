import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import api, fields, models, _
from openerp.exceptions import UserError

from openerp.tools import float_is_zero


class AccountBalanceReport(models.TransientModel):
	_inherit = 'account.balance.report'

	company_id = fields.Many2one('res.company', string='Company', readonly=False, default=lambda self: self.env.user.company_id)

	@api.multi
	def check_report(self):
		res = super(AccountBalanceReport, self).check_report()
		wiz = self.read(['company_id'])[0]['company_id'][0]

		used_context = res['data']['form']['used_context'] or {}
		used_context.update({'company_id':wiz})
		res['data']['form']['used_context']=used_context
		return res

class ReportTrialBalance(models.AbstractModel):
	_inherit = 'report.account.report_trialbalance'

	@api.multi
	def render_html(self, data):
		self.model = self.env.context.get('active_model')
		docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
		display_account = data['form'].get('display_account')
		domain=[]
		company_id = data['form'].get('used_context',False) and data['form'].get('used_context').get('company_id',False)
		if company_id:
			domain.append(('company_id','=',company_id))

		accounts = docs if self.model == 'account.account' else self.env['account.account'].search(domain)
		account_res = self.with_context(data['form'].get('used_context'))._get_accounts(accounts, display_account)

		docargs = {
			'doc_ids': self.ids,
			'doc_model': self.model,
			'data': data['form'],
			'docs': docs,
			'time': time,
			'Accounts': account_res,
		}
		return self.env['report'].with_context({'company_id':company_id}).render('account.report_trialbalance', docargs)

