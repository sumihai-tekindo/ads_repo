# -*- coding: utf-8 -*-

import time
from openerp import api,fields, models

class AccountingReport(models.TransientModel):
	_inherit = "accounting.report"

	company_id = fields.Many2one('res.company', string='Company', readonly=False, default=lambda self: self.env.user.company_id)

	def _build_comparison_context(self, data):
		result = super(AccountingReport, self)._build_comparison_context(data)
		result['company_id'] = 'company_id' in data['form'] and data['form']['company_id'] or self.env.user.company_id.id
		print "--------result---------",result
		return result

	@api.multi
	def check_report(self):
		res = super(AccountingReport, self).check_report()
		data = {}
		data['form'] = self.read(['company_id','account_report_id', 'date_from_cmp', 'date_to_cmp', 'journal_ids', 'filter_cmp', 'target_move'])[0]
		for field in ['account_report_id','company_id']:
			if isinstance(data['form'][field], tuple):
				data['form'][field] = data['form'][field][0]
		comparison_context = self._build_comparison_context(data)
		res['data']['form']['comparison_context'] = comparison_context
		used_context = res['data']['form']['used_context'] or {}
		used_context.update({'company_id':data['form']['company_id']})
		res['data']['form']['used_context']=used_context
		return res

class AccountCommonReport(models.TransientModel):
	_inherit = "account.common.report"

	company_id = fields.Many2one('res.company', string='Company', readonly=False, default=lambda self: self.env.user.company_id)

	def _build_contexts(self, data):
		result = super(AccountCommonReport, self)._build_contexts(data)
		result['company_id'] = 'company_id' in data['form'] and data['form']['company_id'] and data['form']['company_id'][0] or self.env.user.company_id.id
		return result

	@api.multi
	def check_report(self):
		data = super(AccountCommonReport, self).check_report()
		self.ensure_one()
		print error
		data = {}
		data['ids'] = self.env.context.get('active_ids', [])
		data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
		data['form'] = self.read(['company_id','date_from', 'date_to', 'journal_ids', 'target_move'])[0]
		used_context = self._build_contexts(data)
		print "used_context============",used_context
		data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
		return self._print_report(data)

AccountCommonReport()

class ReportFinancial(models.AbstractModel):
	_inherit = 'report.account.report_financial'

	def _compute_account_balance(self, accounts):
		""" compute the balance, debit and credit for the provided accounts
		"""
		mapping = {
			'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
			'debit': "COALESCE(SUM(debit), 0) as debit",
			'credit': "COALESCE(SUM(credit), 0) as credit",
		}
		if self._context.get('company_id',False):
	
			accounts = self.env['account.account'].search([('id','in',[a.id for a in accounts]),('company_id','=',self._context.get('company_id'))])
		res = {}
		for account in accounts:
			res[account.id] = dict((fn, 0.0) for fn in mapping.keys())
		if accounts:
			tables, where_clause, where_params = self.env['account.move.line']._query_get()
			tables = tables.replace('"', '') if tables else "account_move_line"
			wheres = [""]
			if where_clause.strip():
				wheres.append(where_clause.strip())
			filters = " AND ".join(wheres)
			request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
					   " FROM " + tables + \
					   " WHERE account_id IN %s " \
							+ filters + \
					   " GROUP BY account_id"
			params = (tuple(accounts._ids),) + tuple(where_params)
			
			self.env.cr.execute(request, params)
			for row in self.env.cr.dictfetchall():
				res[row['id']] = row
		return res


	def _compute_report_balance(self, reports):
		'''returns a dictionary with key=the ID of a record and value=the credit, debit and balance amount
		   computed for this record. If the record is of type :
			   'accounts' : it's the sum of the linked accounts
			   'account_type' : it's the sum of leaf accoutns with such an account_type
			   'account_report' : it's the amount of the related report
			   'sum' : it's the sum of the children of this record (aka a 'view' record)'''
		
		res = {}
		print "===================",self._context
		company_id = self._context.get('company_id',False)
		context_multicompany = {}
		if company_id:
			context_multicompany.update({'company_id':company_id})
		fields = ['credit', 'debit', 'balance']
		for report in reports:
			if report.id in res:
				continue
			res[report.id] = dict((fn, 0.0) for fn in fields)
			if report.type == 'accounts':
				# it's the sum of the linked accounts
				res[report.id]['account'] = self._compute_account_balance(report.account_ids)
				for value in res[report.id]['account'].values():
					for field in fields:
						res[report.id][field] += value.get(field)
			elif report.type == 'account_type':
				# it's the sum the leaf accounts with such an account type
				accounts = self.env['account.account'].search([('user_type_id', 'in', report.account_type_ids.ids)])
				res[report.id]['account'] = self._compute_account_balance(accounts)
				for value in res[report.id]['account'].values():
					for field in fields:
						res[report.id][field] += value.get(field)
			elif report.type == 'account_report' and report.account_report_id:
				# it's the amount of the linked report
				res2 = self._compute_report_balance(report.account_report_id)
				for key, value in res2.items():
					for field in fields:
						res[report.id][field] += value[field]
			elif report.type == 'sum':
				# it's the sum of the children of this account.report
				res2 = self._compute_report_balance(report.children_ids)
				for key, value in res2.items():
					for field in fields:
						res[report.id][field] += value[field]
		return res