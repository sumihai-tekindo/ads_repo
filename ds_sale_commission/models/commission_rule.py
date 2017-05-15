from openerp.osv import fields,osv

class commission_rule(osv.osv):
	_name="sale.commission.rule"

	_columns = {
		"name": fields.char("Rule Name",required=True),
		"company_id": fields.many2one("res.company","Company",required=True),
		"rule": fields.text("Python Computation Rules",required=True),
		"rule_type": fields.selection([('whs_off','Wholesale Offline'),('whs_on','Wholesale Online'),('ret_off','Retail Offline'),('ret_on','Retail Online')],"Rule Type",required=True),
		"amt_rule": fields.text("Python Commission Rules",required=True),
		"paid_only": fields.boolean("Apply for paid invoice only"),
		"sales_ids": fields.many2many("res.users",'comm_rule_user_rel', 
			'rule_id', 'user_id', 'Salesman'),
		'analytic_ids': fields.many2many("account.analytic.account",'rule_analytic_rel', 
			'rule_id', 'analytic_id', 'Analytic Account'),
	}

	_defaults = {
		"rule":"""#These are the parameters to be used"""
	}