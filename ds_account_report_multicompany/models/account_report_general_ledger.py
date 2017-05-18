import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import api, fields, models, _
from openerp.exceptions import UserError

from openerp.tools import float_is_zero


class AccountReportGeneralLedger(models.TransientModel):
	_inherit = "account.report.general.ledger"

	company_id = fields.Many2one('res.company', string='Company', readonly=False, default=lambda self: self.env.user.company_id)


	@api.multi
	def check_report(self):
		res = super(AccountReportGeneralLedger, self).check_report()
		wiz = self.read(['company_id'])[0]['company_id'][0]

		used_context = res['data']['form']['used_context'] or {}
		used_context.update({'company_id':wiz})
		res['data']['form']['used_context']=used_context
		return res



class ReportGeneralLedger(models.AbstractModel):
	_inherit = 'report.account.report_generalledger'

	@api.multi
	def render_html(self, data):
		self.model = self.env.context.get('active_model')
		docs = self.env[self.model].browse(self.env.context.get('active_ids', []))

		init_balance = data['form'].get('initial_balance', True)
		sortby = data['form'].get('sortby', 'sort_date')
		display_account = data['form']['display_account']
		codes = []

		domain_journal=[('id', 'in', data['form']['journal_ids'])]
		domain=[]
		company_id = data['form'].get('used_context',False) and data['form'].get('used_context').get('company_id',False)
		if company_id:
			domain_journal.append(('company_id','=',company_id))
			domain.append(('company_id','=',company_id))

		if data['form'].get('journal_ids', False):
			codes = [journal.code for journal in self.env['account.journal'].search(domain_journal)]



		accounts = docs if self.model == 'account.account' else self.env['account.account'].search(domain)
		accounts_res = self.with_context(data['form'].get('used_context',{}))._get_account_move_entry(accounts, init_balance, sortby, display_account)
		docargs = {
			'doc_ids': self.ids,
			'doc_model': self.model,
			'data': data['form'],
			'docs': docs,
			'time': time,
			'Accounts': accounts_res,
			'print_journal': codes,
		}
		return self.env['report'].with_context({'company_id':company_id}).render('account.report_generalledger', docargs)