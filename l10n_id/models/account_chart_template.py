# -*- coding: utf-8 -*-

import time
import math

from openerp.osv import expression
from openerp.tools.float_utils import float_round as round
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import AccessError, UserError, ValidationError
import openerp.addons.decimal_precision as dp
from openerp import api, fields, models, _
from openerp import SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)


class AccountChartTemplate(models.Model):
	_inherit = "account.chart.template"


	def _prepare_all_journals(self, acc_template_ref, company, journals_dict=None):
		res = super(AccountChartTemplate,self)._prepare_all_journals(acc_template_ref, company, journals_dict=journals_dict)
		return []

	@api.multi
	def generate_account(self, tax_template_ref, acc_template_ref, code_digits, company):
		""" This method for generating accounts from templates.

			:param tax_template_ref: Taxes templates reference for write taxes_id in account_account.
			:param acc_template_ref: dictionary with the mappping between the account templates and the real accounts.
			:param code_digits: number of digits got from wizard.multi.charts.accounts, this is use for account code.
			:param company_id: company_id selected from wizard.multi.charts.accounts.
			:returns: return acc_template_ref for reference purpose.
			:rtype: dict
		"""
		self.ensure_one()
		account_tmpl_obj = self.env['account.account.template']
		acc_template = account_tmpl_obj.search([('nocreate', '!=', True), ('chart_template_id', '=', self.id)], order='id')
		for account_template in acc_template:
			tax_ids = []
			for tax in account_template.tax_ids:
				tax_ids.append(tax_template_ref[tax.id])

			code_main = account_template.code and len(account_template.code) or 0
			code_acc = account_template.code or ''
			if code_main > 0 and code_main <= code_digits:
				code_acc = str(code_acc) + (str('0'*(code_digits-code_main)))
			vals = {
				'name': account_template.name,
				'currency_id': account_template.currency_id and account_template.currency_id.id or False,
				'code': code_acc,
				'user_type_id': account_template.user_type_id and account_template.user_type_id.id or False,
				'reconcile': account_template.reconcile,
				'note': account_template.note,
				'tax_ids': [(6, 0, tax_ids)],
				'company_id': company.id,
				'company_code':account_template.company_code,
				'tag_ids': [(6, 0, [t.id for t in account_template.tag_ids])],
			}
			new_account = self.env['account.account'].create(vals)
			acc_template_ref[account_template.id] = new_account.id
		return acc_template_ref

class AccountAccountTemplate(models.Model):
	_inherit = "account.account.template"

	company_code = fields.Char('Company Code')