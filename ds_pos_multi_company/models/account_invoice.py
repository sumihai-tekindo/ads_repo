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


class AccountInvoice(models.Model):
	_inherit = "account.invoice"

	online_shop_trans_code = fields.Char("OnlineShop Transaction Code")
	analytic_account_id = fields.Many2one("account.analytic.account",string="Analytic Account")
	payment_journal_ids = fields.One2many('account.journal.invoice.pos','invoice_id',"PoS Payment Journal")


class AccountJournalInvoicePos(models.Model):
	_name="account.journal.invoice.pos"
	
	_rec_name="journal_id"

	journal_id = fields.Many2one("account.journal","Journal")
	amount = fields.Float("Amount")
	invoice_id = fields.Many2one("account.invoice","Invoice")