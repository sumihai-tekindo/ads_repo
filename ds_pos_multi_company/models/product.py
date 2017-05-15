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

class product_template(osv.osv):

	_inherit = "product.template"

	def _get_warehouse_availables(self, cr, uid, ids, name, arg, context=None):
		"""Compute the commitment date"""
		res = {}
		location_ids = self.pool.get('stock.location').search(cr,uid,[('usage','=','internal')])
		products = self.pool.get('product.product').search(cr,uid,[('product_tmpl_id','in',ids)])
		quants = self.pool.get('stock.quant').search(cr,uid,[('product_id','in',products),('location_id','in',location_ids)])
		for prod in self.browse(cr, uid, ids, context=context):
			if prod.id not in res:
				res[prod.id]=[]
		for quant in self.pool.get('stock.quant').browse(cr,uid,quants):
			wh = res.get(quant.product_id.product_tmpl_id.id,[])
			for history in quant.history_ids:
				wh.append(history.warehouse_id.id)
			res[quant.product_id.product_tmpl_id.id]=list(set(wh))
		return res

	def _get_substitutes_qty(self, cr, uid, ids, name, arg, context=None):
		res = {}
		for prod in self.browse(cr,uid,ids,context=context):
			txt = ""
			for sub in prod.substitute_ids:
				txt+="%s : %s\n"%(sub.company_id.name.upper()[:3],sub.qty_available)
			res[prod.id]=txt
		return res

	_columns = {
		"substitute_ids": fields.many2many('product.template', 'product_tmpl_product_rel', 
			'product_tmpl_id', 'substitute_id', 'Substitutes Product Variant in other company'),
		'warehouse_available_ids': fields.function(_get_warehouse_availables,
			string='Warehouse Positions',
			help="The list of warehouse where the product exists.",
			type="many2many", relation="stock.warehouse"),
		'susbtitute_qty': fields.function(_get_substitutes_qty,string="Substitute Qty",type="char"),
	}

	

class product_product(osv.osv):
	_inherit = "product.product"

	def _get_warehouse_availables(self, cr, uid, ids, name, arg, context=None):
		"""Compute the commitment date"""
		res = {}
		location_ids = self.pool.get('stock.location').search(cr,uid,[('usage','=','internal')])
		quants = self.pool.get('stock.quant').search(cr,uid,[('product_id','in',ids),('location_id','in',location_ids)])
		for prod in self.browse(cr, uid, ids, context=context):
			if prod.id not in res:
				res[prod.id]=[]
		for quant in self.pool.get('stock.quant').browse(cr,uid,quants):
			wh = res.get(quant.product_id.id,[])
			for history in quant.history_ids:
				wh.append(history.warehouse_id.id)
			res[quant.product_id.id]=list(set(wh))
		return res
	
	def _get_substitutes_qty(self, cr, uid, ids, name, arg, context=None):
		res = {}
		for prod in self.browse(cr,uid,ids,context=context):
			txt = ""
			for sub in prod.substitute_ids:
				txt+="%s : %s\n"%(sub.company_id.name.upper()[:3],sub.qty_available)
			res[prod.id]=txt
		return res


	_columns = {
		"substitute_ids": fields.many2many('product.product', 'product_product_rel', 
			'product_id', 'substitute_id', 'Substitutes Product in other company'),
		'warehouse_available_ids': fields.function(_get_warehouse_availables,
			string='Warehouse Positions',
			help="The list of warehouse where the product exists.",
			type="many2many", relation="stock.warehouse"),
		'susbtitute_qty': fields.function(_get_substitutes_qty,string="Substitute Qty",type="char"),
	}
