# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import psycopg2
import time
from datetime import datetime
import uuid
import sets

from functools import partial

import openerp
import openerp.addons.decimal_precision as dp
from openerp import tools, models, SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools import float_is_zero
from openerp.tools.translate import _
from openerp.exceptions import UserError

from openerp import api, fields as Fields

_logger = logging.getLogger(__name__)

class pos_config(osv.osv):
	_inherit = "pos.config"

	_columns = {
		'company_ids' : fields.many2many('res.company', 'pos_config_company_rel', 
			'pos_config_id', 'company_id', 'Companies to Show in POS',),
		'account_analytic_ids' : fields.many2many('account.analytic.account', 'pos_config_analytic_rel', 
			'pos_config_id', 'analytic_id', 'Analytic Account to Show in POS'),
		'return_sequence_id' : fields.many2one('ir.sequence', 'Return Order IDs Sequence', readonly=False,
			help="This sequence is automatically created by Odoo but you can change it "\
				"to customize the reference numbers of your orders.", copy=False),
		'sales_ids': fields.many2many('res.users','pos_config_sales_rel','pos_config_id','user_id',"Salesman in PoS")
	}

	# def create(self, cr, uid, values, context=None):
	# 	ir_sequence = self.pool.get('ir.sequence')
	# 	# force sequence_id field to new pos.order sequence
	# 	res = super(pos_config, self).create(cr, uid, values, context=context)
	# 	if res:
	# 		if values.get('sequence_id',False):
	# 			print "--------------",values
	# 			self.write(cr,uid,res,{'sequence_id':values.get('sequence_id',False)})
	# 			return res
	# 		else:
	# 			pos_config_id = self.browse(cr,uid,res)
	# 			r_seq_id = ir_sequence.create(cr, SUPERUSER_ID, {
	# 				'name': 'POS Order Return %s' % values['name'],
	# 				'padding': 6,
	# 				'prefix': "%s/RINV/%%(y)s/"  %(pos_config_id.company_id.name[:3].upper()),
	# 				'code': "pos.order.return",
	# 				'company_id': values.get('company_id', False),
	# 			}, context=context)
	# 			pos_config_id.write({'return_sequence_id':  r_seq_id})
	# 			sequence_id = pos_config_id.sequence_id.write(
	# 					{
	# 					'prefix': "%s/INV/%%(y)s/"  %(pos_config_id.company_id.name[:3].upper()),
	# 					'padding':6,
	# 					})
	# 	return res

	def create(self, cr, uid, values, context=None):
		ir_sequence = self.pool.get('ir.sequence')
		# force sequence_id field to new pos.order sequence
		
		res = super(pos_config, self).create(cr, uid, values, context=context)
		print "--------------",res
		sequence_id = ir_sequence.search(cr,uid,[('code','=','pos.order'),('company_id','=',values.get('company_id',1))],order="id asc",limit=1)
		ret_sequence_id = ir_sequence.search(cr,uid,[('code','=','pos.order.return'),('company_id','=',values.get('company_id',1))],order="id asc",limit=1)
		values['sequence_id']=sequence_id
		values['return_sequence_id']=ret_sequence_id
		pos_config_id = self.browse(cr,uid,res)
		pos_config_id.write({
				'sequence_id':sequence_id and sequence_id[0],
				'return_sequence_id':ret_sequence_id and ret_sequence_id[0]})
		return res