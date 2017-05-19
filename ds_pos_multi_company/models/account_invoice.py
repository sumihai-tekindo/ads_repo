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