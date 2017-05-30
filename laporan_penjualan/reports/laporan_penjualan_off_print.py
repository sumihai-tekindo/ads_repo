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


class laporan_penjualan_off_xls_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(laporan_penjualan_off_xls_parser, self).__init__(cr, uid, name,
                                                         context=context)
        self.context = context
        self.localcontext.update({
            'datetime': datetime,
            'get_invoices':self._get_invoices
        })


    def _get_invoices(self,objects):
        invoices = {}

        for inv in objects:
            if inv.partner_id not in invoices.keys():
                invoices[inv.partner_id]={}
            if inv.partner_id in invoices.keys():
                if not invoices[inv.partner_id].get('wholesale',False):
                    invoices[inv.partner_id]['wholesale']=0.0
                if not invoices[inv.partner_id].get('retail',False):
                    invoices[inv.partner_id]['retail']=0.0

                amt_whs = inv.analytic_account_id and inv.analytic_account_id.sale_type=='wholesale' and (invoices[inv.partner_id]['wholesale']+inv.amount_total) or 0.0
                invoices[inv.partner_id]['wholesale']=amt_whs
                amt_ret = inv.analytic_account_id and inv.analytic_account_id.sale_type=='retail' and (invoices[inv.partner_id]['retail']+inv.amount_total) or 0.0
                invoices[inv.partner_id]['retail']=amt_ret

        return invoices

class laporan_penjualan_off_xls(report_xls):
    
    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(laporan_penjualan_off_xls, self).__init__(
            name, table, rml, parser, header, store)


    def generate_xls_report(self, _p, _xs, data, objects, wb):
        ##Penempatan untuk template rows
        title_style                     = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
        title_style_center                = xlwt.easyxf('font: height 220, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz center; ')
        normal_style                     = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz left;',num_format_str='#,##0.00;-#,##0.00')
        normal_style_center                = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center;')
        normal_style_float                 = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right;',num_format_str='#,##0.00;-#,##0.00')
        normal_style_float_round         = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right;',num_format_str='#,##0')
        normal_style_float_bold         = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz right;',num_format_str='#,##0.00;-#,##0.00')
        normal_bold_style                 = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
        normal_bold_style_a             = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
        normal_bold_style_b             = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on;pattern: pattern solid, fore_color gray25; align: wrap on, vert centre, horiz left; ')
        th_top_style                     = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick')
        th_both_style_left                 = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left;')
        th_both_style                     = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick, bottom thick')
        th_bottom_style                 = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:bottom thick')
        th_both_style_dashed             = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick, bottom dashed',num_format_str='#,##0.00;-#,##0.00')
        th_both_style_dashed_bottom     = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right; border:bottom dashed',num_format_str='#,##0.00;-#,##0.00')
        
        subtotal_title_style            = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz left; borders: top thin, bottom thin;')
        subtotal_style                      = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right; borders: bottom thin;',num_format_str='#,##0;-#,##0')
        subtotal_style2                     = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right; borders: top thin, bottom thin;',num_format_str='#,##0.00;-#,##0.00')
        total_title_style                   = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz left;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;')
        total_style                         = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;',num_format_str='#,##0.0000;(#,##0.0000)')
        total_style2                    = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;',num_format_str='#,##0.00;(#,##0.00)')
        subtittle_top_and_bottom_style  = xlwt.easyxf('font: height 240, name Times New Roman, colour_index black, bold off, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;')
        

        
        ws = wb.add_sheet("Laporan Penjualan Offline")
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        ws.preview_magn = 100
        ws.normal_magn = 100
        ws.print_scaling=100
        ws.page_preview = False
        ws.set_fit_width_to_pages(1)
        
        ws.write_merge(0,0,0,4,"LAPORAN PENJUALAN OFFLINE",title_style_center)
        ws.write_merge(3,3,0,1,"PERIODE",normal_bold_style_a)
        ws.write_merge(3,3,2,4,": "+data['start_date']+" - "+data['end_date'],normal_bold_style_a)
       
        headers = ["No","Nama Customer","Penjualan Wholesale","Penjualan Retail","Total Penjualan Wholesale & retail"]
                   
        col = 0
        for head in headers:
            ws.write(5,col,head,normal_bold_style_b)
            col+=1
            
        no=1
        col = 0
        row=6
        max_len = [int(len(x)*1.5) for x in headers]
        print "maxxxxxxxxxx",max_len
        invoices = _p.get_invoices(objects)
        for rec in invoices:
            ws.write(row,0,no,normal_style_float_round)
            ws.write(row,1,rec.name,normal_style)
            ws.write(row,2,invoices[rec]['wholesale'],normal_style)
            ws.write(row,3,invoices[rec]['retail'],normal_style)
            ws.write(row,4,invoices[rec]['wholesale']+invoices[rec]['retail'],normal_style)
            
            max_len[0]=len(str(no))+3 > max_len[0] and len(str(no))+3 or max_len[0]
            max_len[1]=len(str(rec.name)) > max_len[1] and len(str(rec.name)) or max_len[1]
            max_len[2]=len(str(invoices[rec]['wholesale'])) > max_len[2] and len(str(invoices[rec]['wholesale'])) or max_len[2]
            max_len[3]=len(str(invoices[rec]['retail'])) > max_len[3] and len(str(invoices[rec]['retail'])) or max_len[3]
            max_len[4]=len(str(invoices[rec]['wholesale']+invoices[rec]['retail'])) > max_len[4] and len(str(invoices[rec]['wholesale']+invoices[rec]['retail'])) or max_len[4]
            
            row+=1
            no+=1
            
        for x in range(0,5):
            ws.col(x).width=max_len[x]*256
            

        ws.write_merge(row,row,col,col+1,"TOTAL",title_style)
        ws.write(row,2,xlwt.Formula("SUM($C$7:$C$"+str(row)+")"),subtotal_style2)
        ws.write(row,3,xlwt.Formula("SUM($D$7:$D$"+str(row)+")"),subtotal_style2)
        ws.write(row,4,xlwt.Formula("SUM($E$7:$E$"+str(row)+")"),subtotal_style2)
        
        
laporan_penjualan_off_xls('report.laporan.penjualan.off.xls', 'account.invoice', parser=laporan_penjualan_off_xls_parser)
            
        