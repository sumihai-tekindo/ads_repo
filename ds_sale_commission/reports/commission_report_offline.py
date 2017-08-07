import xlwt
from xlwt import Formula as fm
from datetime import datetime
from openerp.osv import orm
from openerp.addons.report_xls.report_xls import report_xls
# from openerp.addons.report_xls.utils import rowcol_to_cell, _render

import time
from openerp.report import report_sxw
from openerp.tools.translate import translate
import logging

# from .nov_account_journal import nov_journal_print
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class sale_commission_offline_xls_parser(report_sxw.rml_parse):
	
	def __init__(self, cr, uid, name, context):
		super(sale_commission_offline_xls_parser, self).__init__(cr, uid, name, context=context)
		self.context = context
		self.localcontext.update({
			'datetime': datetime,
			'get_user_ids':self._get_user_ids,
			'get_grouped_data': self._get_grouped_data,

		})

	def _get_user_ids(self,objects):
		if objects:
			res =[]
			for x in objects:
				res.append(x.sale_user_id)
			return res
		else:
			
			return []

	def _get_grouped_data(self,objects):
		cr = self.cr
		uid = self.uid
		datas = [x for x in objects]
		# comm_pool = self.pool.get("commission.compute.line.detail")
		res = {}
		for data in datas:
			wholesale= data.rule_type == 'whs_off' and data.amount_total or 0.0
			c_wholesale= data.rule_type == 'whs_off' and data.commission_amount or 0.0
			retail = data.rule_type =='ret_off' and data.amount_total or 0.0
			c_retail = data.rule_type =='ret_off' and data.commission_amount or 0.0

			if data.partner_id not in res:
				res.update({
					data.partner_id:
						{
						'wholesale':wholesale,
						'c_wholesale':c_wholesale,
						'retail':retail,
						'c_retail':c_retail,
						}
					})
			else:
				wholesale0 = res.get(data.partner_id).get('wholesale',0.0)
				c_wholesale0 = res.get(data.partner_id).get('c_wholesale',0.0)
				retail0 = res.get(data.partner_id).get('retail',0.0)
				c_retail0 = res.get(data.partner_id).get('c_retail',0.0)

				wholesale +=wholesale0
				c_wholesale +=c_wholesale0
				retail +=retail0
				c_retail +=c_retail0
				res.update({
						data.partner_id:{
							'wholesale':wholesale,
							'c_wholesale':c_wholesale,
							'retail':retail,
							'c_retail':c_retail,

						}
					})

		return res

class sale_commission_offline_xls(report_xls):
	
	def __init__(self, name, table, rml=False, parser=False, header=True,
				 store=False):
		super(sale_commission_offline_xls, self).__init__(
			name, table, rml, parser, header, store)


	def generate_xls_report(self, _p, _xs, data, objects, wb):
		##Penempatan untuk template rows
		title_style					 = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
		title_style_center			  = xlwt.easyxf('font: height 220, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz center; ')
		normal_style					= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz left;',num_format_str='#,##0.00;-#,##0.00')
		normal_style_center			 = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center;')
		normal_style_float			  = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right;',num_format_str='#,##0.00;-#,##0.00')
		normal_style_float_round		= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right;',num_format_str='#,##0')
		normal_style_float_bold		 = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz right;',num_format_str='#,##0.00;-#,##0.00')
		normal_bold_style			   = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
		normal_bold_style_a			 = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
		normal_bold_style_b			 = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on;pattern: pattern solid, fore_color gray25; align: wrap on, vert centre, horiz left; ')
		th_top_style					 = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick')
		th_both_style_left				 = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left;')
		th_both_style					 = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick, bottom thick')
		th_bottom_style				 = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:bottom thick')
		th_both_style_dashed			 = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick, bottom dashed',num_format_str='#,##0.00;-#,##0.00')
		th_both_style_dashed_bottom	 = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right; border:bottom dashed',num_format_str='#,##0.00;-#,##0.00')
		
		subtotal_title_style			= xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz left; borders: top thin, bottom thin;')
		subtotal_style					  = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right; borders: bottom thin;',num_format_str='#,##0;-#,##0')
		subtotal_style2					 = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right; borders: top thin, bottom thin;',num_format_str='#,##0.00;-#,##0.00')
		total_title_style				   = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz left;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;')
		total_style						 = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;',num_format_str='#,##0.0000;(#,##0.0000)')
		total_style2					= xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;',num_format_str='#,##0.00;(#,##0.00)')
		subtittle_top_and_bottom_style  = xlwt.easyxf('font: height 240, name Times New Roman, colour_index black, bold off, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;')

		# ws = wb.add_sheet("NO DATA FOUND")
		# ws.write_merge(0,0,0,10,"NO DATA FOUND",normal_bold_style_b)

		dummy = _p.get_user_ids(objects)
		print "################",dummy
		if dummy:
			for user_id in dummy:

				ws = wb.add_sheet(user_id.name)
				ws.panes_frozen = True
				ws.remove_splits = True
				ws.portrait = 0  # Landscape
				ws.fit_width_to_pages = 1
				ws.preview_magn = 100
				ws.normal_magn = 100
				ws.print_scaling=100
				ws.page_preview = False
				ws.set_fit_width_to_pages(1)
				
				ws.write_merge(0,0,0,4,"Laporan Komisi Penjualan Offline",title_style_center)
				ws.write_merge(3,3,0,1,"Salesman",normal_bold_style_a)
				ws.write_merge(4,4,2,4,": %s"%user_id.name,normal_bold_style_a)
				
				ws.write_merge(4,4,0,1,"PERIODE",normal_bold_style_a)
				ws.write_merge(4,4,2,4,": "+data['date_start']+" - "+data['date_end'],normal_bold_style_a)
			
				headers = ["No","Customer","Penjualan Wholesale","Komisi Wholesale","Penjualan Retail","Komisi Retail"]
				val_head = ['partner_id',"wholesale",'c_wholesale',"retail","c_retail"]
				col = 0
				for head in headers:
					ws.write(6,col,head,normal_bold_style_b)
					col+=1
					
				no=1
				col = 0
				row=7
				row=7
				max_len = [int(len(x)*1.5) for x in headers]

				grouped_data = _p.get_grouped_data(objects,user_id.id)

				for rec in grouped_data:
					partner_id = rec.name
					wholesale = grouped_data.get(rec).get('wholesale',0.0)
					c_wholesale = grouped_data.get(rec).get('c_wholesale',0.0)
					retail = grouped_data.get(rec).get('retail',0.0)
					c_retail = grouped_data.get(rec).get('c_retail',0.0)
									
					for co in range(0,len(val_head)):
						ws.write(row,co+1,eval(val_head[co]),normal_style_float)
					row+=1

				ws.write_merge(row,row,0,1,"TOTAL",title_style)
				ws.write(row,2,xlwt.Formula("SUM($C$7:$C$"+str(row)+")"),subtotal_style2)
				ws.write(row,3,xlwt.Formula("SUM($D$7:$D$"+str(row)+")"),subtotal_style2)
				ws.write(row,4,xlwt.Formula("SUM($E$7:$E$"+str(row)+")"),subtotal_style2)

			else:
				print "==================",dummy
				ws = wb.add_sheet("NO DATA FOUND")
				ws.write_merge(0,0,0,10,"NO DATA FOUND",normal_bold_style_b)				
sale_commission_offline_xls('report.sale.commission.offline.xls', 'commission.compute.line.detail', parser=sale_commission_offline_xls_parser)