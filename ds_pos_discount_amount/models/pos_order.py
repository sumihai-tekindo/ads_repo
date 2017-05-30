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

class pos_order_line(osv.osv):
	_inherit="pos.order.line"
	
	discount_amt = Fields.Float("Discount Amount 2nd Level",help="This discount is given as second level discount using amount")
	price_subtotal = Fields.Float(compute='_compute_amount_line_all', digits=0, string='Subtotal w/o Tax')
	price_subtotal_incl = Fields.Float(compute='_compute_amount_line_all', digits=0, string='Subtotal')

	def onchange_product_id(self, cr, uid, ids, pricelist, product_id, qty=0, partner_id=False, context=None):
		res = super(pos_order_line,self).onchange_product_id(cr,uid,ids,pricelist,product_id,qty=qty,partner_id=partner_id,context=context)
		if res.get('value',False):
			val = res.get('value',{})
			val.update({'discount_amt':0.0})
			res.update({'value':val})
		return res

	# @api.onchange('discount_amt')
	# def onchange_discount_amt(self,):
	# 	if self.discount_amt:
	# 		dummy = self.discount_amt
	# 		val = self.onchange_product_id().get('value',False)
	# 		if val:
	# 			fields = val.keys()
	# 			for x in fields:
	# 				eval("self."+x+"=val.get("+x+")")
	# 			self.discount_amt = dummy	

	@api.depends('price_unit', 'tax_ids', 'qty', 'discount','discount_amt', 'product_id')
	def _compute_amount_line_all(self):

		for line in self:
			currency = line.order_id.pricelist_id.currency_id
			taxes = line.tax_ids.filtered(lambda tax: tax.company_id.id == line.order_id.company_id.id)
			fiscal_position_id = line.order_id.fiscal_position_id
			if fiscal_position_id:
				taxes = fiscal_position_id.map_tax(taxes)

			price = (((line.price_unit * (1 - (line.discount or 0.0) / 100.0) )*line.qty)-line.discount_amt)/line.qty
			line.price_subtotal = line.price_subtotal_incl = price * line.qty
			if taxes:

				taxes = taxes.compute_all(price, currency, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
				
				line.price_subtotal = taxes['total_excluded']
				line.price_subtotal_incl = taxes['total_included']

			line.price_subtotal = currency.round(line.price_subtotal)
			line.price_subtotal_incl = currency.round(line.price_subtotal_incl)

class pos_order(osv.osv):
	_inherit = "pos.order"
	
	total_discount = Fields.Float(compute='_compute_amount_all', digits=0, string='Total Discount Given')
	amount_tax = Fields.Float(compute='_compute_amount_all', string='Taxes', digits=0)
	amount_total = Fields.Float(compute='_compute_amount_all', string='Total', digits=0)
	amount_paid = Fields.Float(compute='_compute_amount_all', string='Paid', states={'draft': [('readonly', False)]}, readonly=True, digits=0)
	amount_return = Fields.Float(compute='_compute_amount_all', string='Returned', digits=0)

	def _amount_line_tax(self, cr, uid, line, fiscal_position_id, context=None):
		taxes = line.tax_ids.filtered(lambda t: t.company_id.id == line.order_id.company_id.id)
		if fiscal_position_id:
			taxes = fiscal_position_id.map_tax(taxes)
		price = (((line.price_unit * (1 - (line.discount or 0.0) / 100.0))*line.qty)-line.discount_amt)/line.qty
		cur = line.order_id.pricelist_id.currency_id
		taxes = taxes.compute_all(price, cur, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)['taxes']
		val = 0.0
		for c in taxes:
			val += c.get('amount', 0.0)
		return val
	

	@api.depends('statement_ids', 'lines.price_subtotal_incl', 'lines.discount','lines.discount_amt')
	def _compute_amount_all(self):
		for order in self:
			order.amount_paid = order.amount_return = order.amount_tax = 0.0
			currency = order.pricelist_id.currency_id
			order.amount_paid = sum(payment.amount for payment in order.statement_ids)
			order.amount_return = sum(payment.amount < 0 and payment.amount or 0 for payment in order.statement_ids)
			order.amount_tax = currency.round(sum(self._amount_line_tax(line, order.fiscal_position_id) for line in order.lines))
			amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))
			order.total_discount = currency.round(sum(line.discount_amt for line in order.lines))
			order.amount_total = order.amount_tax + amount_untaxed

	def create_picking(self, cr, uid, ids, context=None):
		"""Create a picking for each order and validate it."""
		picking_obj = self.pool.get('stock.picking')
		partner_obj = self.pool.get('res.partner')
		move_obj = self.pool.get('stock.move')

		for order in self.browse(cr, uid, ids, context=context):
			if all(t == 'service' for t in order.lines.mapped('product_id.type')):
				continue
			addr = order.partner_id and partner_obj.address_get(cr, uid, [order.partner_id.id], ['delivery']) or {}
			picking_type = order.picking_type_id
			return_pick_type = order.picking_type_id.return_picking_type_id or order.picking_type_id
			order_picking_id = False
			return_picking_id = False
			location_id = order.location_id.id
			if order.partner_id:
				destination_id = order.partner_id.property_stock_customer.id
			else:
				if (not picking_type) or (not picking_type.default_location_dest_id):
					customerloc, supplierloc = self.pool['stock.warehouse']._get_partner_locations(cr, uid, [], context=context)
					destination_id = customerloc.id
				else:
					destination_id = picking_type.default_location_dest_id.id

			# Create the normal use case picking (Stock -> Customer)
			if picking_type:
				picking_vals = {
					'origin': order.name,
					'partner_id': addr.get('delivery', False),
					'date_done': order.date_order,
					'picking_type_id': picking_type.id,
					'company_id': order.company_id.id,
					'move_type': 'direct',
					'note': order.note or "",
					'location_id': location_id,
					'location_dest_id': destination_id,
				}
				pos_qty = any([x.qty >= 0 for x in order.lines])
				if pos_qty:
					order_picking_id = picking_obj.create(cr, uid, picking_vals.copy(), context=context)
				neg_qty = any([x.qty < 0 for x in order.lines])
				if neg_qty:
					return_vals = picking_vals.copy()
					return_vals.update({
						'location_id': destination_id,
						'location_dest_id': location_id,
						'picking_type_id': return_pick_type.id
					})
					return_picking_id = picking_obj.create(cr, uid, return_vals, context=context)

			move_list = []
			for line in order.lines:
				if line.product_id and line.product_id.type not in ['product', 'consu']:
					continue
				move_id = move_obj.create(cr, uid, {
					'name': line.name,
					'product_uom': line.product_id.uom_id.id,
					'picking_id': order_picking_id if line.qty >= 0 else return_picking_id,
					'picking_type_id': picking_type.id if line.qty >= 0 else return_pick_type.id,
					'product_id': line.product_id.id,
					'product_uom_qty': abs(line.qty),
					'state': 'draft',
					'location_id': location_id if line.qty >= 0 else destination_id,
					'location_dest_id': destination_id if line.qty >= 0 else location_id,
				}, context=context)
				move_list.append(move_id)

			# prefer associating the regular order picking, not the return
			self.write(cr, uid, [order.id], {'picking_id': order_picking_id or return_picking_id}, context=context)

			if return_picking_id:
				self._force_picking_done(cr, uid, return_picking_id, context=context)
			if order_picking_id:
				self._force_picking_done(cr, uid, order_picking_id, context=context)

			# when the pos.config has no picking_type_id set only the moves will be created
			if move_list and not return_picking_id and not order_picking_id:
				move_obj.action_confirm(cr, uid, move_list, context=context)
				move_obj.force_assign(cr, uid, move_list, context=context)
				active_move_list = [x.id for x in move_obj.browse(cr, uid, move_list, context=context) if x.product_id.tracking == 'none']
				if active_move_list:
					move_obj.action_done(cr, uid, active_move_list, context=context)

		return True

	def _prepare_analytic_account(self, cr, uid, line, context=None):
		'''This method is designed to be inherited in a custom module'''
		res = super(pos_order,self)._prepare_analytic_account( cr, uid, line, context=context)
		return line.order_id and line.order_id.analytic_account_id and line.order_id.analytic_account_id.id or False

	def action_invoice(self, cr, uid, ids, context=None):
		inv_ref = self.pool.get('account.invoice')
		inv_line_ref = self.pool.get('account.invoice.line')
		product_obj = self.pool.get('product.product')
		inv_ids = []

		for order in self.pool.get('pos.order').browse(cr, uid, ids, context=context):
			# Force company for all SUPERUSER_ID action
			company_id = order.company_id.id
			local_context = dict(context or {}, force_company=company_id, company_id=company_id)
			if order.invoice_id:
				inv_ids.append(order.invoice_id.id)
				continue

			if not order.partner_id:
				raise UserError(_('Please provide a partner for the sale.'))

			acc = order.partner_id.property_account_receivable_id.id
			inv = {
				'name': order.name,
				'origin': order.name,
				'account_id': acc,
				'online_shop_trans_code': order.online_shop_trans_code or False,
				'analytic_account_id':self._prepare_analytic_account(cr, uid, order.lines[0], context=local_context),
				'journal_id': order.sale_journal.id or None,
				'type': 'out_invoice',
				'reference': order.name,
				'partner_id': order.partner_id.id,
				'comment': order.note or '',
				'currency_id': order.pricelist_id.currency_id.id, # considering partner's sale pricelist's currency
				'company_id': company_id,
				'user_id': (order.user_id and order.user_id.id) or (order.pos_admin and order.pos_admin.id),
				'payment_journal_ids':False,
			}
			invoice = inv_ref.new(cr, uid, inv)
			invoice._onchange_partner_id()
			invoice.fiscal_position_id = order.fiscal_position_id
			

			inv = invoice._convert_to_write(invoice._cache)
			if not inv.get('account_id', None):
				inv['account_id'] = acc
			payment_journal_ids =[]
			for s in order.statement_ids:
				if s.amount!=0.0:
					payment_journal_ids.append((0,0,{'journal_id':s.journal_id.id,'amount':s.amount}))

			inv.update({'payment_journal_ids':payment_journal_ids})
			inv_id = inv_ref.create(cr, SUPERUSER_ID, inv, context=local_context)

			self.write(cr, uid, [order.id], {'invoice_id': inv_id, 'state': 'invoiced'}, context=local_context)
			inv_ids.append(inv_id)
			for line in order.lines:
				inv_name = product_obj.name_get(cr, uid, [line.product_id.id], context=local_context)[0][1]
				inv_line = {
					'invoice_id': inv_id,
					'product_id': line.product_id.id,
					'quantity': line.qty,
					'account_analytic_id': self._prepare_analytic_account(cr, uid, line, context=local_context),
					'name': inv_name,
					'discount_amount': line.discount_amt,
				}

				#Oldlin trick
				invoice_line = inv_line_ref.new(cr, SUPERUSER_ID, inv_line, context=local_context)
				invoice_line._onchange_product_id()
				invoice_line.invoice_line_tax_ids = [tax.id for tax in invoice_line.invoice_line_tax_ids if tax.company_id.id == company_id]
				fiscal_position_id = line.order_id.fiscal_position_id
				if fiscal_position_id:
					invoice_line.invoice_line_tax_ids = fiscal_position_id.map_tax(invoice_line.invoice_line_tax_ids)
				invoice_line.invoice_line_tax_ids = [tax.id for tax in invoice_line.invoice_line_tax_ids]
				# We convert a new id object back to a dictionary to write to bridge between old and new api
				inv_line = invoice_line._convert_to_write(invoice_line._cache)
				inv_line.update(price_unit=line.price_unit, discount=line.discount)
				inv_line_ref.create(cr, SUPERUSER_ID, inv_line, context=local_context)
			inv_ref.compute_taxes(cr, SUPERUSER_ID, [inv_id], context=local_context)
			self.signal_workflow(cr, uid, [order.id], 'invoice')
			inv_ref.signal_workflow(cr, SUPERUSER_ID, [inv_id], 'validate')

		if not inv_ids: return {}

		mod_obj = self.pool.get('ir.model.data')
		res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
		res_id = res and res[1] or False
		return {
			'name': _('Customer Invoice'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': [res_id],
			'res_model': 'account.invoice',
			'context': "{'type':'out_invoice'}",
			'type': 'ir.actions.act_window',
			'target': 'current',
			'res_id': inv_ids and inv_ids[0] or False,
		}