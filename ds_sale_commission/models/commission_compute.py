from openerp.osv import fields,osv

class commission_compute(osv.osv):
	_name="commission.compute"

	_columns = {
		"name": fields.char("Number",required=True),
		"start_date": fields.date("Start Date",required=True),
		"company_id": fields.many2one('res.company',"Company",required=True),
		"end_date"	: fields.date("End Date",required=True),
		"line_ids"	: fields.one2many("commission.compute.line","comm_id","Commission Lines"),

	}

	def compute(self,cr,uid,ids,context=None):
		if not context:context={}
		invoice_pool = self.pool.get('account.invoice')
		comm_rule = self.pool.get('sale.commission.rule')
		comm_line_pool = self.pool.get('commission.compute.line')
		for comm in self.browse(cr,uid,ids,context=context):
			if comm.line_ids:
				comm_line_pool.unlink(cr,uid,[x.id for x in comm.line_ids])
			rule_ids = comm_rule.search(cr,uid,[('company_id','=',comm.company_id.id)])
			rules = comm_rule.browse(cr,uid,rule_ids)
			invoice_ids = invoice_pool.search(cr,uid,[('state','in',['open','paid']),('company_id','=',comm.company_id.id),('date_invoice','>=',comm.start_date),('date_invoice','<=',comm.end_date),('type','=','out_invoice')])
			comm_lines = {}
			for inv in invoice_pool.browse(cr,uid,invoice_ids):
				amount_total = inv.amount_total
				amount_untaxed = inv.amount_untaxed
				analytic_account_ids = inv.invoice_line_ids and inv.invoice_line_ids[0].account_analytic_id and inv.invoice_line_ids[0].account_analytic_id.id or False
				user_id = inv.user_id and inv.user_id.id
				state = inv.state
				for rule in rules:
					sales_ids = [s.id for s in rule.sales_ids]
					analytic_ids = [s.id for s in rule.analytic_ids]
					paid_rule=False
					if rule.paid_only:
						paid_rule = inv.state=='paid' or False
					else:
						paid_rule = True
					apply_rule = paid_rule and eval(rule.rule)
					print "=============",apply_rule
					if apply_rule:
						commission_amount = eval(rule.amt_rule)
						if user_id in comm_lines:
							if comm_lines.get(user_id,False) and comm_lines.get(user_id).get(rule.rule_type,False):
								comm_amt=comm_lines.get(user_id).get(rule_type).get('commission_amount',0.0)
								comm_amt+=commission_amount
								sale_amt=comm_lines.get(user_id).get(rule_type).get('amount_total',0.0)
								sale_amt+=commission_amount
								untaxed_amt=comm_lines.get(user_id).get(rule_type).get('amount_untaxed',0.0)
								untaxed_amt+=commission_amount
								comm_lines[user_id][rule.rule_type]['commission_amount']=comm_amt
								comm_lines[user_id][rule.rule_type]['amount_total']=sale_amt
								comm_lines[user_id][rule.rule_type]['amount_untaxed']=untaxed_amt
							else:
								comm_lines[user_id][rule.rule_type]['commission_amount']=commission_amount
								comm_lines[user_id][rule.rule_type]['amount_total']=amount_total
								comm_lines[user_id][rule.rule_type]['amount_untaxed']=amount_untaxed
						else:
							comm_lines.update({
								user_id:{rule.rule_type:{
														'commission_amount': commission_amount,
														'amount_total': amount_total,
														'amount_untaxed': amount_untaxed
														}}
								}) 
						break
					else:
						continue
			for cl in comm_lines:

				for cluse in comm_lines.get(cl):
					user = comm_lines.get(cl).get(cluse)
					print "===========",user
					cl_val = {
						'comm_id':comm.id,
						'sale_user_id':cl,
						'rule_type': cluse,
						'commission_amount':user.get('commission_amount',0.0),
						'amount_total':user.get('amount_total',0.0),
						'amount_untaxed':user.get('amount_untaxed',0.0),
					}
					comm_line_pool.create(cr,uid,cl_val)
		return True
class commission_compute_line(osv.osv):
	_name="commission.compute.line"

	_columns={
		"comm_id": fields.many2one("commission.compute","Commission Computation",required=True),
		"rule_type": fields.selection([('whs_off','Wholesale Offline'),('whs_on','Wholesale Online'),('ret_off','Retail Offline'),('ret_on','Retail Online')],"Rule Type",required=True),
		"sale_user_id": fields.many2one("res.users","Salesperson",required=True),
		"commission_amount": fields.float("Commission Amount",required=True),
		"amount_total": fields.float("Sale Amount",required=True),
		"amount_untaxed": fields.float("Untaxed Amount",required=True),
	}

	_defaults = {
		"commission_amount": 0.0,
		"amount_total": 0.0,
		"amount_untaxed": 0.0,
	}