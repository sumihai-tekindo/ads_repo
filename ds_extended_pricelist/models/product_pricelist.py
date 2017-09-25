from itertools import chain
import time

from openerp import tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.osv import fields, osv
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError
from openerp import api, models, fields as Fields

#----------------------------------------------------------
# Price lists
#----------------------------------------------------------

class product_pricelist(osv.osv):
	_inherit = "product.pricelist"

	def _price_rule_get_multi(self, cr, uid, pricelist, products_by_qty_by_partner, context=None):
		context = context or {}
		date = context.get('date') and context['date'][0:10] or time.strftime(DEFAULT_SERVER_DATE_FORMAT)
		products = map(lambda x: x[0], products_by_qty_by_partner)
		product_uom_obj = self.pool.get('product.uom')

		if not products:
			return {}

		categ_ids = {}
		for p in products:
			categ = p.categ_id
			while categ:
				categ_ids[categ.id] = True
				categ = categ.parent_id
		categ_ids = categ_ids.keys()

		is_product_template = products[0]._name == "product.template"
		if is_product_template:
			prod_tmpl_ids = [tmpl.id for tmpl in products]
			# all variants of all products
			prod_ids = [p.id for p in
						list(chain.from_iterable([t.product_variant_ids for t in products]))]
		else:
			prod_ids = [product.id for product in products]
			prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

		# Load all rules
		cr.execute(
			'SELECT i.id '
			'FROM product_pricelist_item AS i '
			'LEFT JOIN product_category AS c '
			'ON i.categ_id = c.id '
			'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = any(%s))'
			'AND (product_id IS NULL OR product_id = any(%s))'
			'AND (categ_id IS NULL OR categ_id = any(%s)) '
			'AND (pricelist_id = %s) '
			'AND ((i.date_start IS NULL OR i.date_start<=%s) AND (i.date_end IS NULL OR i.date_end>=%s))'
			'ORDER BY applied_on, min_quantity desc, c.parent_left desc',
			(prod_tmpl_ids, prod_ids, categ_ids, pricelist.id, date, date))

		item_ids = [x[0] for x in cr.fetchall()]
		items = self.pool.get('product.pricelist.item').browse(cr, uid, item_ids, context=context)
		results = {}
		for product, qty, partner in products_by_qty_by_partner:
			results[product.id] = 0.0
			suitable_rule = False

			# Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
			# An intermediary unit price may be computed according to a different UoM, in
			# which case the price_uom_id contains that UoM.
			# The final price will be converted to match `qty_uom_id`.
			qty_uom_id = context.get('uom') or product.uom_id.id
			price_uom_id = product.uom_id.id
			qty_in_product_uom = qty
			if qty_uom_id != product.uom_id.id:
				try:
					qty_in_product_uom = product_uom_obj._compute_qty(
						cr, uid, context['uom'], qty, product.uom_id.id)
				except UserError:
					# Ignored - incompatible UoM in context, use default product UoM
					pass

			# if Public user try to access standard price from website sale, need to call _price_get.
			price = self.pool['product.template']._price_get(cr, uid, [product], 'list_price', context=context)[product.id]

			price_uom_id = qty_uom_id
			for rule in items:
				if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
					continue
				if is_product_template:
					if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
						continue
					if rule.product_id and not (product.product_variant_count == 1 and product.product_variant_ids[0].id == rule.product_id.id):
						# product rule acceptable on template if has only one variant
						continue
				else:
					if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
						continue
					if rule.product_id and product.id != rule.product_id.id:
						continue

				if rule.categ_id:
					cat = product.categ_id
					while cat:
						if cat.id == rule.categ_id.id:
							break
						cat = cat.parent_id
					if not cat:
						continue

				if rule.base == 'pricelist' and rule.base_pricelist_id:
					price_tmp = self._price_get_multi(cr, uid, rule.base_pricelist_id, [(product, qty, partner)], context=context)[product.id]
					ptype_src = rule.base_pricelist_id.currency_id.id
					price = self.pool['res.currency'].compute(cr, uid, ptype_src, pricelist.currency_id.id, price_tmp, round=False, context=context)
				else:
					# if base option is public price take sale price else cost price of product
					# price_get returns the price in the context UoM, i.e. qty_uom_id
					price = self.pool['product.template']._price_get(cr, uid, [product], rule.base, context=context)[product.id]

				base_price = self.pool['product.template']._price_get(cr, uid, [product], 'list_price', context=context)[product.id]
				cost_price = self.pool['product.template']._price_get(cr, uid, [product], 'standard_price', context=context)[product.id]
				other_pricelist_price=price

				if rule.python_pricelist_id and rule.python_pricelist_id.id:
					price_tmp = self._price_get_multi(cr, uid, rule.python_pricelist_id, [(product, qty, partner)], context=context)[product.id]
					ptype_src = rule.python_pricelist_id.currency_id.id
					price = self.pool['res.currency'].compute(cr, uid, ptype_src, pricelist.currency_id.id, price_tmp, round=False, context=context)
					other_pricelist_price=price

				convert_to_price_uom = (lambda price: product_uom_obj._compute_price(
											cr, uid, product.uom_id.id,
											price, price_uom_id))

				if price is not False:
					if rule.compute_price == 'fixed':
						price = convert_to_price_uom(rule.fixed_price)
					elif rule.compute_price == 'percentage':
						price = (price - (price * (rule.percent_price / 100))) or 0.0
					elif rule.compute_price == 'formula':
						#complete formula
						price_limit = price
						price = (price - (price * (rule.price_discount / 100))) or 0.0
						if rule.price_round:
							price = tools.float_round(price, precision_rounding=rule.price_round)

						if rule.price_surcharge:
							price_surcharge = convert_to_price_uom(rule.price_surcharge)
							price += price_surcharge

						if rule.price_min_margin:
							price_min_margin = convert_to_price_uom(rule.price_min_margin)
							price = max(price, price_limit + price_min_margin)

						if rule.price_max_margin:
							price_max_margin = convert_to_price_uom(rule.price_max_margin)
							price = min(price, price_limit + price_max_margin)
					else:

						try:
							# print "xxxxxxxxxxxxxxxxxxxxxxxx",rule.python_formula
							price=eval(rule.python_formula)
						except:
							price=price
					suitable_rule = rule
				break
			# Final price conversion into pricelist currency
			if suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
				price = self.pool['res.currency'].compute(cr, uid, product.currency_id.id, pricelist.currency_id.id, price, round=False, context=context)

			results[product.id] = (price, suitable_rule and suitable_rule.id or False)
		return results


class product_pricelist_item(osv.osv):
	_inherit ="product.pricelist.item"
	_columns = {
		'compute_price': fields.selection([('fixed', 'Fix Price'), ('percentage', 'Percentage (discount)'), ('formula', 'Formula'),('python','Python Formula')], select=True, default='fixed'),
		'python_formula': fields.text("Python Formula"),
		'python_pricelist_id': fields.many2one('product.pricelist', 'Other Pricelist for python Formula', ondelete='cascade', select=True),
	}

	_defaults = {
		"python_formula":"""#Use these following fields for the formula: base_price, cost_price and other_pricelist_price"""
	}

