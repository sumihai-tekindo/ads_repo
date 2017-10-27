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
from openerp import workflow
from openerp import api, fields as Fields

_logger = logging.getLogger(__name__)

class pos_order(osv.osv):
	_inherit = "pos.order"

	_columns = {
		'online_shop_trans_code': fields.char("OnlineShop Transaction Code"),
		'analytic_account_id': fields.many2one("account.analytic.account","Analytic Account"),
		'pos_admin': fields.many2one('res.users',"PoS Admin"),
	}

	def _order_fields(self, cr, uid, ui_order, context=None):
		res=super(pos_order,self)._order_fields(cr, uid, ui_order, context=context)
		res.update({
				'online_shop_trans_code':ui_order['online_shop_trans_code'] or False,
				'analytic_account_id':ui_order['analytic_account_id'] or False,
				'pos_admin':ui_order['pos_admin'] or False,
				})
		return res

	def _default_purchase_picking_type(self,cr,uid,context=None):
		type_obj = self.pool.get('stock.picking.type')
		company_id = context.get('company_id') or self.pool.get('res.users').browse(cr,uid,uid,context=context).company_id.id
		types = type_obj.search(cr,uid,[('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
		if not types:
			types = type_obj.search(cr,uid,[('code', '=', 'incoming'), ('warehouse_id', '=', False)])
		return types[:1]

	def _default_sale_warehouse(self,cr,uid,context=None):
		wh_obj = self.pool.get('stock.warehouse')
		company_id = context.get('company_id')
		return wh_obj.search(cr,uid,[('company_id', '=', company_id)], limit=1)
	

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
				'user_admin_id': (order.pos_admin and order.pos_admin.id) or (order.user_id and order.user_id.id),
				'payment_journal_ids':False
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

	def create_internal_transactions(self,cr,uid,order,context=None):
		if order and order['lines']:
			session_id=order['pos_session_id']
			session=self.pool.get('pos.session').browse(cr,uid,session_id)
			to_create = {}
			for line in order['lines']:
				if line[2]['company_substitute_id'] and int(line[2]['company_substitute_id'])!=session.config_id.company_id.id:
					prod=self.pool.get('product.product').browse(cr,uid,line[2]['product_id'])
					sub_id = False

					for sub in prod.substitute_ids:
						if sub.company_id.id == int(line[2]['company_substitute_id']):
							sub_id=sub
					if not sub_id:
						raise UserError(_('Configuration error!\nThere is no substitute products defined for product variant id %s - %s.')%(prod.id,prod.name_get()[0][2]))
					if int(line[2]['company_substitute_id']) not in to_create.keys():
						to_create.update({int(line[2]['company_substitute_id']):[{'product_id':prod,'substitute_id':sub_id,'product_qty':line[2]['qty'],'price_unit':line[2]['price_unit']}]})
					else:
						dummy = to_create.get(int(line[2]['company_substitute_id']),[])
						dummy.append({'product_id':line[2]['product_id'],'substitute_id':sub_id,'product_qty':line[2]['qty'],'price_unit':line[2]['price_unit']})
						to_create.update({int(line[2]['company_substitute_id']):dummy})
			pos_company = session.config_id.company_id
			for tc in to_create:
				company = self.pool.get('res.company').browse(cr,uid,tc)


				partner_id = company.partner_id.id
				pricelist_id =session.config_id.pricelist_id
				related_pricelist = False
				for pl in pricelist_id.substitute_ids:
					if pl.company_id.id==tc:
						related_pricelist=pl.id

				#create sale order
				ctx_sale={'company_id':tc,'force_company':tc}
				warehouse_id = self._default_sale_warehouse(cr,uid,context=ctx_sale)
				sale = {
					'partner_id' 		: pos_company.partner_id.id,
					'pricelist_id'		: related_pricelist,
					'date_order' 		: order['creation_date'],
					'company_id' 		: tc,
					'client_order_ref'	: order['name'],
					'picking_policy'	: 'direct',
					'order_line'		: [],
				}
				sale_order_line = []
				for so_line in to_create[tc]:

					try:
						so_line_product_uom_sub = so_line['substitute_id'].uom_id.id
						substitute_product_id = so_line['substitute_id'].id
					except:
						prod_s_check = self.pool.get('product.product').browse(cr,uid,so_line['substitute_id'])
						so_line_product_uom_sub = prod_s_check.uom_id.id
						substitute_product_id = so_line['substitute_id']
					product_context = {
							'lang': pos_company.partner_id.lang,
							'partner': pos_company.partner_id.id,
							'quantity': so_line['product_qty'],
							'date':order['creation_date'],
							'pricelist':related_pricelist,
							'uom_id':so_line_product_uom_sub,
							}
					product_sub=self.pool.get('product.product').browse(cr,uid,substitute_product_id,context=product_context)

					name = product_sub.name_get()[0][1]
	
					if product_sub.description_sale:
						name += '\n' + product_sub.description_sale

					try:
						product_uom = so_line['product_id'].uom_po_id.id or so_line['product_id'].uom_id.id
					except:
						product_check = self.pool.get('product.product').browse(cr,uid,so_line['product_id'])
						product_uom = product_check.uom_po_id.id or product_check.uom_id.id

					sale_order_line.append((0,0,{
						'product_id'		:product_sub.id,
						'name'				:name,
						'date_planned'		:order['creation_date'],
						'product_uom_qty'		:so_line['product_qty'],
						'product_uom'		:product_uom,
						'price_unit'		:product_sub.price >1.0 or so_line['price_unit'],
						}))
					so_line.update({'price_unit':product_sub.price >1.0 or so_line['price_unit'] })

				sale.update({'order_line':sale_order_line})

				sale_id = self.pool.get('sale.order').create(cr,uid,sale)
				sale_order = self.pool.get('sale.order').browse(cr,uid,sale_id,context=context)

				sale_order.write({'warehouse_id':warehouse_id[0]})
				#confirm sale order


				self.pool.get('sale.order').action_confirm(cr,uid,sale_id,context=context)
				sale_order = self.pool.get('sale.order').browse(cr,uid,sale_id,context=context)

				#confirm delivery order only draft (newly created)
				
				pick_ids = sale_order.picking_ids

				for pick_id in pick_ids:
					if pick_id.state == 'draft':
						pick_id.action_confirm()
						if pick_id.state != 'assigned':
							pick_id.action_assign()
							if pick_id.state != 'assigned':
								raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
					for pack in pick_id.pack_operation_ids:
						if pack.product_qty > 0:
							pack.write({'qty_done': pack.product_qty})
						else:
							pack.unlink()


				doid = self.pool.get('stock.picking').do_transfer(cr,uid,[p.id for p in pick_ids])

				#create customer invoice
				local_context = dict(context or {}, force_company=tc, company_id=tc)
				so_inv_ids=self.pool.get('sale.order').action_invoice_create(cr,uid,sale_id,context=local_context)
				journal_sale = self.pool.get('account.journal').search(cr,uid,[('company_id','=',tc),('type','=','sale')],limit=1,order="id asc")
				
				partner_so = self.pool.get('res.partner').browse(cr,uid,company.partner_id.id,context=local_context)
				acc_receivable_so = partner_so.property_account_receivable_id.id

				self.pool.get('account.invoice').write(cr,uid,so_inv_ids,{'journal_id':journal_sale[0],'company_id':tc,
					'account_id':acc_receivable_so},context=local_context)

				# print "=======journal=======>",company.name,acc_receivable_so
				
				# release customer invoices
				for inv in so_inv_ids:
					# print "inv-----------------",inv
					workflow.trg_validate(uid, 'account.invoice', inv, 'invoice_open', cr)


				#create purchase order
				ctx_purchase={'company_id':pos_company.id}
				picking_type_id = self._default_purchase_picking_type(cr,uid,context=ctx_purchase)
				purchase = {
					'partner_id' 	: partner_id,
					'date_order' 	: order['creation_date'],
					'company_id' 	: session.config_id.company_id.id,
					'partner_ref'	: order['name'],
					'date_planned'	: order['creation_date'],
					'order_line'	: [],
				}
				purchase_order_line = []
				for po_line in to_create[tc]:
					try:
						name = po_line['product_id'].name_get()[0][1]
					except:
						prod_po_check = self.pool.get('product.product').browse(cr,uid,po_line['product_id'])
						name = prod_po_check.name_get()[0][1]
					try:	
						if po_line['product_id'].description_sale:
							name += '\n' + po_line['product_id'].description_sale
					except:
						if prod_po_check.description_sale:
							name += '\n' + prod_po_check.description_sale
					try:
						purchase_order_line.append((0,0,{
							'product_id'		:po_line['product_id'].id,
							'name'				:name,
							'date_planned'		:order['creation_date'],
							'product_qty'		:po_line['product_qty'],
							'product_uom'		:po_line['product_id'].uom_po_id.id or po_line['product_id'].uom_id.id,
							'price_unit'		:po_line['price_unit']
							}))
					except:
						purchase_order_line.append((0,0,{
							'product_id'		:prod_po_check.id,
							'name'				:name,
							'date_planned'		:order['creation_date'],
							'product_qty'		:po_line['product_qty'],
							'product_uom'		:prod_po_check.uom_po_id.id or prod_po_check.uom_id.id,
							'price_unit'		:po_line['price_unit']
							}))

				purchase.update({'order_line':purchase_order_line})
				po_id = self.pool.get('purchase.order').create(cr,uid,purchase)
				#confirm purchase order
				self.pool.get('purchase.order').button_confirm(cr,uid,po_id,context=context)
				#confirm goods receipt/incoming shipment
				purchase_order = self.pool.get('purchase.order').browse(cr,uid,po_id,context=context)
				incomings = purchase_order.picking_ids

				for pick_id in incomings:
					if pick_id.state == 'draft':
						pick_id.action_confirm()
						if pick_id.state != 'assigned':
							pick_id.action_assign()
							if pick_id.state != 'assigned':
								raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
					for pack in pick_id.pack_operation_ids:
						if pack.product_qty > 0:
							pack.write({'qty_done': pack.product_qty})
						else:
							pack.unlink()

				rec_id = self.pool.get('stock.picking').do_transfer(cr,uid,[p.id for p in incomings])
				#create supplier invoice from PO
				ctx_supp_inv={'type':'in_invoice','company_id':session.config_id.company_id.id,'force_company':session.config_id.company_id.id}
				supp_inv_journal_id = self.pool.get('account.invoice')._default_journal(cr,uid,context=ctx_supp_inv)
				supp_inv = {
					'partner_id':partner_id,
					'date_invoice':order['creation_date'],
					'date_due':order['creation_date'],
					'journal_id':supp_inv_journal_id.id,
					'account_id':session.config_id.company_id.partner_id.property_account_payable_id.id,
					'purchase_id':po_id,
				}
				supp_inv_id = self.pool.get('account.invoice').create(cr,uid,supp_inv,context=ctx_supp_inv)
				supp_inv_data = self.pool.get('account.invoice').browse(cr,uid,supp_inv_id)
				supp_inv_data.purchase_order_change()
				# for inv in supp_inv_id:

				workflow.trg_validate(uid, 'account.invoice', supp_inv_id, 'invoice_open', cr)


		return True
	def create_from_ui(self, cr, uid, orders, context=None):
		submitted_references = [o['data']['name'] for o in orders]
		existing_order_ids = self.search(cr, uid, [('pos_reference', 'in', submitted_references)], context=context)
		existing_orders = self.read(cr, uid, existing_order_ids, ['pos_reference'], context=context)
		existing_references = set([o['pos_reference'] for o in existing_orders])
		orders_to_save = [o for o in orders if o['data']['name'] not in existing_references]

		order_ids = []

		for tmp_order in orders_to_save:
			order = tmp_order['data']
			internal_transaction = self.create_internal_transactions(cr,uid,order,context=context)
		res = super(pos_order,self).create_from_ui(cr,uid,orders,context=context)
		return res


class pos_order_line(osv.osv):
	_inherit = "pos.order.line"
	_columns = {
		"company_substitute_id": fields.many2one('res.company',"Company Substitute Product"),
	}

	def _order_line_fields(self, cr, uid, line, context=None):
		line = super(pos_order_line,self)._order_line_fields(cr, uid, line, context=context)
		
		return line