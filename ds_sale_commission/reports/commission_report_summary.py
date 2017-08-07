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


class sale_commission_summary_xls_parser(report_sxw.rml_parse):
	
	def __init__(self, cr, uid, name, context):
		super(sale_commission_summary_xls_parser, self).__init__(cr, uid, name, context=context)
		self.context = context
		self.localcontext.update({
			'datetime': datetime,
			'get_user_ids':self._get_user_ids,
			'get_grouped_data': self._get_grouped_data,

		})

	def _get_user_ids(self,objects):
		return list(set([x.sale_user_id for x in objects]))
	
	def _get_grouped_data(self,objects,user_id):
		cr = self.cr
		uid = self.uid
		datas = [x for x in objects if x.sale_user_id==user_id]
		# comm_pool = self.pool.get("commission.compute.line.detail")
		res = {}
		for data in datas:
			wholesale_on= data.rule_type == 'whs_on' and data.amount_total or 0.0
			c_wholesale_on= data.rule_type == 'whs_on' and data.commission_amount or 0.0
			retail_on = data.rule_type =='ret_on' and data.amount_total or 0.0
			c_retail_on = data.rule_type =='ret_on' and data.commission_amount or 0.0
			wholesale_off= data.rule_type == 'whs_off' and data.amount_total or 0.0
			c_wholesale_off= data.rule_type == 'whs_off' and data.commission_amount or 0.0
			retail_off = data.rule_type =='ret_off' and data.amount_total or 0.0
			c_retail_off = data.rule_type =='ret_off' and data.commission_amount or 0.0

			if data.sale_user_id not in res:
				res.update({
					data.partner_id:
						{
						'wholesale_on':wholesale_on,
						'c_wholesale_on':c_wholesale_on,
						'retail_on':retail_on,
						'c_retail_on':c_retail_on,
						'wholesale_off':wholesale_off,
						'c_wholesale_off':c_wholesale_off,
						'retail_off':retail_off,
						'c_retail_off':c_retail_off,
						}
					})
			else:
				wholesale_on0 = res.get(data.partner_id).get('wholesale_on',0.0)
				c_wholesale_on0 = res.get(data.partner_id).get('c_wholesale_on',0.0)
				retail_on0 = res.get(data.partner_id).get('retail_on',0.0)
				c_retail_on0 = res.get(data.partner_id).get('c_retail_on',0.0)
				wholesale_off0 = res.get(data.partner_id).get('wholesale_off',0.0)
				c_wholesale_off0 = res.get(data.partner_id).get('c_wholesale_off',0.0)
				retail_off0 = res.get(data.partner_id).get('retail_off',0.0)
				c_retail_off0 = res.get(data.partner_id).get('c_retail_off',0.0)

				wholesale_on +=wholesale_on0
				c_wholesale_on +=c_wholesale_on0
				retail_on +=retail_on0
				c_retail_on +=c_retail_on0
				wholesale_off +=wholesale_off0
				c_wholesale_off +=c_wholesale_off0
				retail_off +=retail_off0
				c_retail_off +=c_retail_off0
				total=c_wholesale_on+c_retail_on+c_wholesale_off+c_retail_off
		return res

class sale_commission_summary_xls(report_xls):
	
	def __init__(self, name, table, rml=False, parser=False, header=True,
				 store=False):
		super(sale_commission_summary_xls, self).__init__(
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
		


		ws = wb.add_sheet("Komisi Sales")
		ws.panes_frozen = True
		ws.remove_splits = True
		ws.portrait = 0  # Landscape
		ws.fit_width_to_pages = 1
		ws.preview_magn = 100
		ws.normal_magn = 100
		ws.print_scaling=100
		ws.page_preview = False
		ws.set_fit_width_to_pages(1)
		ws.write_merge(0,0,0,4,"Laporan Komisi Penjualan Summary",title_style_center)
		
		# ws.write_merge(3,3,0,1,"Salesman",normal_bold_style_a)
		# ws.write_merge(4,4,2,4,": %s"%user_id.name,normal_bold_style_a)
		
		ws.write_merge(4,4,0,1,"PERIODE",normal_bold_style_a)
		ws.write_merge(4,4,2,4,": "+data['date_start']+" - "+data['date_end'],normal_bold_style_a)
		
		ws.write_merge(6,7,0,0,"No",normal_bold_style_b)
		ws.write_merge(6,7,1,1,"Salesman",normal_bold_style_b)
		ws.write_merge(6,6,2,5,"Penjualan Online",normal_bold_style_b)
		ws.write_merge(6,6,6,9,"Penjualan Offline",normal_bold_style_b)
		ws.write_merge(6,7,10,10,"Total Komisi",normal_bold_style_b)
		ws.write(7,7,2,2,"Penjualan Wholesale",normal_bold_style_b)
		ws.write(7,7,3,3,"Komisi Wholesale",normal_bold_style_b)
		ws.write(7,7,4,4,"Penjualan Retail",normal_bold_style_b)
		ws.write(7,7,5,5,"Komisi Retail",normal_bold_style_b)
		ws.write(7,7,6,6,"Penjualan Wholesale",normal_bold_style_b)
		ws.write(7,7,7,7,"Komisi Wholesale",normal_bold_style_b)
		ws.write(7,7,8,8,"Penjualan Retail",normal_bold_style_b)
		ws.write(7,7,9,9,"Komisi Retail",normal_bold_style_b)


		val_head = ["salesman","whs_on","c_whs_on","ret_on","c_ret_on","whs_off","c_whs_off","ret_off","c_ret_off","total"]
		
		no=1
		col = 0
		row=8
		row=8
		max_len = [int(len(x)*1.5) for x in headers]

		grouped_data = _p.get_grouped_data(objects)
		if grouped_data:
			for rec in grouped_data:
				salesman = rec.name
				whs_on = grouped_data.get(rec).get('wholesale_on',0.0)
				c_whs_on = grouped_data.get(rec).get('c_wholesale_on',0.0)
				ret_on = grouped_data.get(rec).get('retail_on',0.0)
				c_ret_on = grouped_data.get(rec).get('c_retail_on',0.0)
				whs_off = grouped_data.get(rec).get('wholesale_off',0.0)
				c_whs_off = grouped_data.get(rec).get('c_wholesale_off',0.0)
				ret_off = grouped_data.get(rec).get('retail_off',0.0)
				c_ret_off = grouped_data.get(rec).get('c_retail_off',0.0)
				total = grouped_data.get(rec).get('c_retail_off',0.0)

				for co in range(0,len(val_head)):
					ws.write(row,co+1,eval(val_head[co]),normal_style_float)
				row+=1

			ws.write_merge(row,row,0,1,"TOTAL",title_style)
			ws.write(row,2,xlwt.Formula("SUM($C$7:$C$"+str(row)+")"),subtotal_style2)
			ws.write(row,3,xlwt.Formula("SUM($D$7:$D$"+str(row)+")"),subtotal_style2)
			ws.write(row,4,xlwt.Formula("SUM($E$7:$E$"+str(row)+")"),subtotal_style2)
			ws.write(row,5,xlwt.Formula("SUM($F$7:$F$"+str(row)+")"),subtotal_style2)
			ws.write(row,6,xlwt.Formula("SUM($G$7:$G$"+str(row)+")"),subtotal_style2)
			ws.write(row,7,xlwt.Formula("SUM($H$7:$H$"+str(row)+")"),subtotal_style2)
			ws.write(row,8,xlwt.Formula("SUM($I$7:$I$"+str(row)+")"),subtotal_style2)
			ws.write(row,9,xlwt.Formula("SUM($J$7:$J$"+str(row)+")"),subtotal_style2)
			ws.write(row,10,xlwt.Formula("SUM($K$7:$K$"+str(row)+")"),subtotal_style2)

		else:
			ws.write_merge(row,row+2,0,10,"NO DATA",normal_style_center)
		
sale_commission_summary_xls('report.sale.commission.summary.xls', 'commission.compute.line.detail', parser=sale_commission_summary_xls_parser)