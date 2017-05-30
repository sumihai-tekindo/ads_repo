from openerp.osv import fields,osv

class commission_compute(osv.osv):
	_name="commission.compute"

	_columns = {
		"name": fields.char("Number",required=True),
		"start_date": fields.date("Start Date",required=True),
		"company_id": fields.many2one('res.company',"Company",required=True),
		"end_date"	: fields.date("End Date",required=True),
		"line_ids"	: fields.one2many("commission.compute.line","comm_id","Commission Lines"),
		"line_detail_ids"	: fields.one2many("commission.compute.line.detail","comm_id","Commission Detail Lines"),
	}

	def compute(self,cr,uid,ids,context=None):
		if not context:context={}
		invoice_pool = self.pool.get('account.invoice')
		comm_rule = self.pool.get('sale.commission.rule')
		comm_line_pool = self.pool.get('commission.compute.line')
		comm_line_detail_pool = self.pool.get('commission.compute.line.detail')
		for comm in self.browse(cr,uid,ids,context=context):
			if comm.line_ids:
				comm_line_pool.unlink(cr,uid,[x.id for x in comm.line_ids])
			if comm.line_detail_ids:
				comm_line_detail_pool.unlink(cr,uid,[x.id for x in comm.line_detail_ids])
			rule_ids = comm_rule.search(cr,uid,[('company_id','=',comm.company_id.id)])
			rules = comm_rule.browse(cr,uid,rule_ids)
			invoice_ids = invoice_pool.search(cr,uid,[('state','in',['open','paid']),('company_id','=',comm.company_id.id),('date_invoice','>=',comm.start_date),('date_invoice','<=',comm.end_date),('type','=','out_invoice')])
			comm_lines = {}
			comm_detail = {}
			for inv in invoice_pool.browse(cr,uid,invoice_ids):
				amount_total = inv.amount_total
				amount_untaxed = inv.amount_untaxed
				analytic_account_ids = inv.invoice_line_ids and inv.invoice_line_ids[0].account_analytic_id and inv.invoice_line_ids[0].account_analytic_id.id or []
				user_id = inv.user_id and inv.user_id.id
				state = inv.state
				payment_journal = inv.payment_journal_ids and inv.payment_journal_ids[0] and inv.payment_journal_ids[0].journal_id.id or inv.journal_id.id
				for rule in rules:
					sales_ids = [s.id for s in rule.sales_ids]
					analytic_ids = [s.id for s in rule.analytic_ids]
					paid_rule=False
					if user_id ==1:
						print "analytic_account_ids",amount_total,amount_untaxed
					if rule.paid_only:
						paid_rule = inv.state=='paid' or False
					else:
						paid_rule = True
					apply_rule = paid_rule and eval(rule.rule)
					if apply_rule:
						commission_amount = eval(rule.amt_rule)

						##apply comm_lines
						if user_id in comm_lines:
							if comm_lines.get(user_id,False) and comm_lines.get(user_id).get(rule.rule_type,False):
								comm_amt=comm_lines.get(user_id).get(rule.rule_type).get('commission_amount',0.0)
								comm_amt+=commission_amount
								sale_amt=comm_lines.get(user_id).get(rule.rule_type).get('amount_total',0.0)
								sale_amt+=amount_total
								untaxed_amt=comm_lines.get(user_id).get(rule.rule_type).get('amount_untaxed',0.0)
								untaxed_amt+=amount_untaxed
								comm_lines[user_id][rule.rule_type]['commission_amount']=comm_amt
								comm_lines[user_id][rule.rule_type]['amount_total']=sale_amt
								comm_lines[user_id][rule.rule_type]['amount_untaxed']=untaxed_amt
							else:
								comm_lines.get(user_id)[rule.rule_type]={}
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

						##apply comm_detail
						
						if user_id not in comm_detail:
							comm_detail.update({
									user_id:{
											rule.rule_type:{
													payment_journal:{
																	inv.partner_id.id:{
																					'commission_amount': commission_amount,
																					'amount_total': amount_total,
																					'amount_untaxed': amount_untaxed
																						}
																				}
															}
											}
										})
						else:
							if not comm_detail[user_id].get(rule.rule_type,False):
								comm_detail[user_id].update({
											rule.rule_type:{
													payment_journal:{
																	inv.partner_id.id:{
																					'commission_amount': commission_amount,
																					'amount_total': amount_total,
																					'amount_untaxed': amount_untaxed
																						}
																				}
															}
											})
							else:
								if not comm_detail[user_id][rule.rule_type].get(payment_journal,False):
									comm_detail[user_id][rule.rule_type].update({
													payment_journal:{
																	inv.partner_id.id:{
																					'commission_amount': commission_amount,
																					'amount_total': amount_total,
																					'amount_untaxed': amount_untaxed
																						}
																				}
											})
								else:
									if not comm_detail[user_id][rule.rule_type][payment_journal].get(inv.partner_id.id,False):
										comm_detail[user_id][rule.rule_type][payment_journal].update({
																	inv.partner_id.id:{
																					'commission_amount': commission_amount,
																					'amount_total': amount_total,
																					'amount_untaxed': amount_untaxed
																						}
											})
									else:
										comm_amt=comm_detail[user_id][rule.rule_type][payment_journal][inv.partner_id.id].get('commission_amount',0.0)
										comm_amt+=commission_amount
										sale_amt=comm_detail[user_id][rule.rule_type][payment_journal][inv.partner_id.id].get('amount_total',0.0)
										sale_amt+=amount_total
										untaxed_amt=comm_detail[user_id][rule.rule_type][payment_journal][inv.partner_id.id].get('amount_untaxed',0.0)
										untaxed_amt+=amount_untaxed
										comm_detail[user_id][rule.rule_type][payment_journal][inv.partner_id.id]['commission_amount']=comm_amt
										comm_detail[user_id][rule.rule_type][payment_journal][inv.partner_id.id]['amount_total']=sale_amt
										comm_detail[user_id][rule.rule_type][payment_journal][inv.partner_id.id]['amount_untaxed']=untaxed_amt

						break
					else:
						continue
			for cl in comm_lines:

				for cluse in comm_lines.get(cl):
					user = comm_lines.get(cl).get(cluse)
					cl_val = {
						'comm_id':comm.id,
						'sale_user_id':cl,
						'rule_type': cluse,
						'commission_amount':user.get('commission_amount',0.0),
						'amount_total':user.get('amount_total',0.0),
						'amount_untaxed':user.get('amount_untaxed',0.0),
					}
					comm_line_pool.create(cr,uid,cl_val)

			for cl2 in comm_detail:
				sale_user_id = cl2
				for clrule in comm_detail[sale_user_id]:
					crule =clrule
					for toko in comm_detail[sale_user_id][crule]:
						for partner in comm_detail[sale_user_id][crule][toko]:
							cl_val_detail = {
								'comm_id':comm.id,
								'sale_user_id':sale_user_id,
								'rule_type': crule,
								'journal_id': toko,
								'partner_id':partner,
								'commission_amount':comm_detail[sale_user_id][crule][toko][partner].get('commission_amount',0.0),
								'amount_total':comm_detail[sale_user_id][crule][toko][partner].get('amount_total',0.0),
								'amount_untaxed':comm_detail[sale_user_id][crule][toko][partner].get('amount_untaxed',0.0),
							}
							comm_line_detail_pool.create(cr,uid,cl_val_detail)
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
		'start_date': fields.related('comm_id', 'start_date', type='date', string='Start Date', store=True, readonly=True),
		'end_date': fields.related('comm_id', 'end_date', type='date', string='End Date', store=True, readonly=True),
		'company_id': fields.related('comm_id', 'company_id', type='many2one',relation="res.company", string='Company', store=True, readonly=True),
	}

	_defaults = {
		"commission_amount": 0.0,
		"amount_total": 0.0,
		"amount_untaxed": 0.0,
	}

class commission_compute_line_detail(osv.osv):
	_name="commission.compute.line.detail"

	_columns={
		"comm_id": fields.many2one("commission.compute","Commission Computation",required=True),
		"partner_id" : fields.many2one('res.partner',"Customer",required=True),
		"rule_type": fields.selection([('whs_off','Wholesale Offline'),('whs_on','Wholesale Online'),('ret_off','Retail Offline'),('ret_on','Retail Online')],"Rule Type",required=True),
		"sale_user_id": fields.many2one("res.users","Salesperson",required=True),
		"commission_amount": fields.float("Commission Amount",required=True),
		"amount_total": fields.float("Sale Amount",required=True),
		"amount_untaxed": fields.float("Untaxed Amount",required=True),
		"journal_id": fields.many2one("account.journal","Journal",required=True),
		'start_date': fields.related('comm_id', 'start_date', type='date', string='Start Date', store=True, readonly=True),
		'end_date': fields.related('comm_id', 'end_date', type='date', string='End Date', store=True, readonly=True),
		'company_id': fields.related('comm_id', 'company_id', type='many2one',relation="res.company", string='Company', store=True, readonly=True),
	}

	_defaults = {
		"commission_amount": 0.0,
		"amount_total": 0.0,
		"amount_untaxed": 0.0,
	}