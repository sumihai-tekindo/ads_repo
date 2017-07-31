from openerp.osv import fields,osv

class equity_available(osv.osv):
	_name = "equity.available"
	_columns = {
		"name": fields.many2one("res.partner","Equity Partner"),
		"equity_account_id": fields.many2one("account.account","Equity Account",required=True),
		"prive_account": fields.many2one("account.account","Prive Account",required=True),
		"company_id": fields.many2one("res.company","Company",required=True),
		"pl_account_id": fields.many2one("account.account","P/L Account",required=True),
	}

class equity_change_wizard(osv.osv_memory):
	_name="equity.change.wizard"
	_columns = {
		"date_start": fields.date("Start Date",required=True),
		"date_end"	: fields.date("End Date",required=True),
		"company_id": fields.many2one("res.company","Company",required=True),
		}

	def print_report(self,cr,uid,ids,context=None):
		if not context:context={}
		wiz = self.browse(cr,uid,ids,context=context)
		if wiz.company_id and wiz.date_start and wiz.date_end:
			avas = self.pool.get("equity.available").search(cr,uid,[('company_id','=',wiz.company_id.id)])
			
		datas={
			'model'	: 'equity.available',
			"ids"	: avas, 
			'date_start':wiz.date_start,
			'date_end':wiz.date_end,
		}
		return{
			'type': 'ir.actions.report.xml',
			'report_name': 'equity.change.xls',
			'datas': datas
		}  