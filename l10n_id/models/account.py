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


class AccountAccount(models.Model):
    _inherit = "account.account"

    company_code = fields.Char('Company Code')
