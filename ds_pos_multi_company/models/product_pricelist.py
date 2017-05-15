from openerp.osv import osv,fields

class product_pricelist(osv.osv):
	_inherit="product.pricelist"
	_columns = {
		"substitute_ids": fields.many2many('product.pricelist', 'pricelist_pricelist_rel', 
			'pricelist_id', 'substitute_id', 'Intercompany Transaction Pricelist in other company'),
	}