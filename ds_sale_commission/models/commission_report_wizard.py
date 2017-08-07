from openerp.osv import fields,osv

class commission_report_wizard(osv.osv_memory):
	_name = "commission.report.wizard"

	_columns ={
		"date_start"	: fields.date("Date Start",required=True),
		"date_end"		: fields.date("Date End",required=True),
		"sale_type"		: fields.selection([('online','Online'),('offline','Offline'),('summary','Summary')],"Sale Type",required=True),
		"company_id"	: fields.many2one("res.company","Company",required=True),
		"user_ids"		: fields.many2many('res.users', 'comm_wiz_user_rel', 
			'wiz_id', 'user_id', 'Sales Users',),
	}

	def print_report(self,cr,uid,ids,context=None):
		if not context:context={}
		wiz = self.browse(cr,uid,ids,context=context)
		comm_pool=self.pool.get("commission.compute.line.detail")
		if wiz.sale_type=='online':
			rule_type=['whs_on','ret_on']
		else:
			rule_type=['whs_off','ret_off']

		if wiz.company_id and wiz.date_start and wiz.date_end:
			comm_detail_ids = comm_pool.search(cr,uid,[('company_id','=',wiz.company_id.id),('start_date','=',wiz.date_start),
				('end_date','=',wiz.date_end),('sale_user_id','in',[x.id for x in wiz.user_ids]),('rule_type','in',rule_type)])
			
		datas={
			'model'	: 'commission.compute.line.detail',
			"ids"	: comm_detail_ids, 
			'date_start':wiz.date_start,
			'date_end':wiz.date_end,
		}
		if wiz.sale_type=='online':
			return{
				'type': 'ir.actions.report.xml',
				'report_name': 'sale.commission.online.xls',
				'datas': datas
			}  
		elif wiz.sale_type=='offline':
			return{
				'type': 'ir.actions.report.xml',
				'report_name': 'sale.commission.offline.xls',
				'datas': datas
			}
		else:
			return{
				'type': 'ir.actions.report.xml',
				'report_name': 'sale.commission.summary.xls',
				'datas': datas
			}