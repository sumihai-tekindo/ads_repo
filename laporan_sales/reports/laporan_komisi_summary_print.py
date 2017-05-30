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

# from .nov_account_partner import nov_partner_print
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class laporan_comm_summary_xls_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(laporan_comm_summary_xls_parser, self).__init__(cr, uid, name,
                                                         context=context)
        self.context = context
        self.localcontext.update({
            'datetime': datetime,
            'group_data':self._group_data
        })


    def _group_data(self,objects):
        # print "-----------------",objects
        commissions = {}
        for comm in objects:
            
            amt_on_whs = comm.rule_type=='whs_on' and comm.amount_untaxed or 0.0
            comm_on_whs = comm.rule_type=='whs_on' and comm.commission_amount or 0.0
            amt_on_ret = comm.rule_type=='ret_on' and comm.amount_untaxed or 0.0 
            comm_on_ret = comm.rule_type=='ret_on' and comm.commission_amount or 0.0
            amt_of_whs = comm.rule_type=='whs_off' and comm.amount_untaxed or 0.0
            comm_of_whs = comm.rule_type=='whs_off' and comm.commission_amount or 0.0
            amt_of_ret = comm.rule_type=='ret_off' and comm.amount_untaxed or 0.0 
            comm_of_ret = comm.rule_type=='ret_off' and comm.commission_amount or 0.0
            
            if comm.sale_user_id not in commissions:
                commissions.update({comm.sale_user_id:{'wholesale':{'amt_on_whs':amt_on_whs,'comm_on_whs':comm_on_whs,'amt_of_whs':amt_of_whs,'comm_of_whs':comm_of_whs},'retail':{'amt_on_ret':amt_on_ret,'comm_on_ret':comm_on_ret,'amt_of_ret':amt_of_ret,'comm_of_ret':comm_of_ret}}})
            else:
                if comm.rule_type in ('whs_on','whs_off') and comm.rule_type not in commissions[comm.sale_user_id]:
                    commissions[comm.sale_user_id]['wholesale'].update({'amt_on_whs':amt_on_whs,'comm_on_whs':comm_on_whs,'amt_of_whs':amt_of_whs,'comm_of_whs':comm_of_whs})
                elif comm.rule_type in ('ret_on','ret_off') and comm.rule_type not in commissions[comm.sale_user_id]:
                    commissions[comm.sale_user_id]['retail'].update({'amt_on_ret':amt_on_ret,'comm_on_ret':comm_on_ret,'amt_of_ret':amt_of_ret,'comm_of_ret':comm_of_ret})
                else:
                    amt_on_whs+=commissions[comm.sale_user_id]['wholesale']['amt_on_whs']
                    amt_of_whs+=commissions[comm.sale_user_id]['wholesale']['amt_of_whs']
                    comm_on_whs+=commissions[comm.sale_user_id]['wholesale']['comm_on_whs']
                    comm_of_whs+=commissions[comm.sale_user_id]['wholesale']['comm_of_whs']
                    amt_on_ret+=commissions[comm.sale_user_id]['retail']['amt_on_ret']
                    amt_of_ret+=commissions[comm.sale_user_id]['retail']['amt_of_ret']
                    comm_on_ret+=commissions[comm.sale_user_id]['retail']['comm_on_ret']
                    comm_of_ret+=commissions[comm.sale_user_id]['retail']['commission']
                    commissions[comm.sale_user_id]['wholesale'].update({'amt_on_whs':amt_on_whs,'comm_on_whs':comm_on_whs,'amt_of_whs':amt_of_whs,'comm_of_whs':comm_of_whs})
                    commissions[comm.sale_user_id]['retail'].update({'amt_on_ret':amt_on_ret,'comm_on_ret':comm_on_ret,'amt_of_ret':amt_of_ret,'comm_of_ret':comm_of_ret})
        return commissions

class laporan_comm_summary_xls(report_xls):
    
    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(laporan_comm_summary_xls, self).__init__(
            name, table, rml, parser, header, store)


    def generate_xls_report(self, _p, _xs, data, objects, wb):
       
        
        
        ##Penempatan untuk template rows
        title_style                     = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
        title_style_center              = xlwt.easyxf('font: height 220, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz center; ')
        normal_style                    = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz left;',num_format_str='#,##0.00;-#,##0.00')
        normal_style_center             = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center;')
        normal_style_float              = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right;',num_format_str='#,##0.00;-#,##0.00')
        normal_style_float_round        = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right;',num_format_str='#,##0')
        normal_style_float_bold         = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz right;',num_format_str='#,##0.00;-#,##0.00')
        normal_bold_style               = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
        normal_bold_style_a             = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
        normal_bold_style_b             = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on;pattern: pattern solid, fore_color gray25; align: wrap on, vert centre, horiz left; ')
        normal_bold_style_b             = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on;pattern: pattern solid, fore_color gray25; align: wrap on, vert centre, horiz left; ')
        th_top_style                    = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick')
        th_both_style_left              = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left;')
        th_both_style                   = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick, bottom thick')
        th_bottom_style                 = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:bottom thick')
        th_both_style_dashed            = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick, bottom dashed',num_format_str='#,##0.00;-#,##0.00')
        th_both_style_dashed_bottom     = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right; border:bottom dashed',num_format_str='#,##0.00;-#,##0.00')
        
        subtotal_title_style            = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz left; borders: top thin, bottom thin;')
        subtotal_style                  = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right; borders: bottom thin;',num_format_str='#,##0;-#,##0')
        subtotal_style2                 = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right; borders: top thin, bottom thin;',num_format_str='#,##0.00;-#,##0.00')
        total_title_style               = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz left;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;')
        total_style                     = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;',num_format_str='#,##0.0000;(#,##0.0000)')
        total_style2                    = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;',num_format_str='#,##0.00;(#,##0.00)')
        subtittle_top_and_bottom_style  = xlwt.easyxf('font: height 240, name Times New Roman, colour_index black, bold off, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;')
        
        border_all                      = xlwt.easyxf('border:top thick, bottom thick, left thick, right thick')
        bold_border_all                 = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz center;pattern: pattern solid, fore_color gray25; border:top thin, bottom thin, left thin, right thin')
        
        
        
        
        ws = wb.add_sheet("Rekapitulasi Komisi")
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        ws.preview_magn = 100
        ws.normal_magn = 100
        ws.print_scaling=100
        ws.page_preview = False
        ws.set_fit_width_to_pages(1)
        
        ws.write_merge(0,0,0,6,"LAPORAN REKAPITULASI KOMISI",title_style_center)
                    
        ws.write_merge(3,3,0,1,"Tanggal",normal_bold_style_a)
        ws.write_merge(3,3,2,4,": "+data['start_date']+" - "+data['end_date'],normal_bold_style_a)     
       
           
            
        col = 0
        row=5
        ws.write_merge(row,row+1,0,0,"NO",bold_border_all)
        ws.write_merge(row,row+1,1,1,"NAMA SALES",bold_border_all)
        ws.write_merge(row,row,2,5,"PENJUALAN ONLINE",bold_border_all)
        ws.write_merge(row,row,6,9,"PENJUALAN OFFLINE",bold_border_all)
        ws.write_merge(row,row+1,10,10,"TOTAL KOMISI",bold_border_all)
        row+=1
        ws.write(row,2,"PENJUALAN WHOLESALE",bold_border_all)
        ws.write(row,3,"KOMISI WHOLESALE",bold_border_all)
        ws.write(row,4,"PENJUALAN RETAIL",bold_border_all)
        ws.write(row,5,"KOMISI RETAIL",bold_border_all)
        ws.write(row,6,"PENJUALAN WHOLESALE",bold_border_all)
        ws.write(row,7,"KOMISI WHOLESALE",bold_border_all)
        ws.write(row,8,"PENJUALAN RETAIL",bold_border_all)
        ws.write(row,9,"KOMISI RETAIL",bold_border_all)

        row+=1
        header=["NO","NAMA SALES","PENJUALAN WHOLESALE","KOMISI WHOLESALE","PENJUALAN RETAIL","KOMISI RETAIL","PENJUALAN WHOLESALE","KOMISI WHOLESALE","PENJUALAN RETAIL","KOMISI RETAIL"]
        max_len = [int(len(x)*1.5) for x in header]
        grouped_data = _p.group_data(objects)

        # amt_on_whs = comm.rule_type=='whs_on' and comm.amount_untaxed or 0.0
        # comm_on_whs = comm.rule_type=='whs_on' and comm.commission_amount or 0.0
        # amt_on_ret = comm.rule_type=='ret_on' and comm.amount_untaxed or 0.0 
        # comm_on_ret = comm.rule_type=='ret_on' and comm.commission_amount or 0.0
        # amt_of_whs = comm.rule_type=='whs_on' and comm.amount_untaxed or 0.0
        # comm_of_whs = comm.rule_type=='whs_on' and comm.commission_amount or 0.0
        # amt_of_ret = comm.rule_type=='ret_on' and comm.amount_untaxed or 0.0 
        # comm_of_ret = comm.rule_type=='ret_on' and comm.commission_amount or 0.0
        no=1

        for sales in grouped_data:  
            ws.write(row,0,no,normal_style_float_round)
            ws.write(row,1,sales.name,normal_style)
            
            ws.write(row,2,grouped_data[sales]['wholesale']['amt_on_whs'],normal_style_float)
            ws.write(row,3,grouped_data[sales]['wholesale']['comm_on_whs'],normal_style_float)
            ws.write(row,4,grouped_data[sales]['retail']['amt_on_ret'],normal_style_float)
            ws.write(row,5,grouped_data[sales]['retail']['comm_on_ret'],normal_style_float)
            ws.write(row,6,grouped_data[sales]['wholesale']['amt_of_whs'],normal_style_float)
            ws.write(row,7,grouped_data[sales]['wholesale']['comm_of_whs'],normal_style_float)
            ws.write(row,8,grouped_data[sales]['retail']['amt_of_ret'],normal_style_float)
            ws.write(row,9,grouped_data[sales]['retail']['comm_of_ret'],normal_style_float)
            subtotal_row=grouped_data[sales]['wholesale']['comm_on_whs']+grouped_data[sales]['retail']['comm_on_ret']+grouped_data[sales]['wholesale']['comm_of_whs']+grouped_data[sales]['retail']['comm_of_ret']
            ws.write(row,10,subtotal_row,normal_style_float)
           
            max_len[0]=len(str(no))+3 > max_len[0] and len(str(no))+3 or max_len[0]
            max_len[1]=len(str(sales.name)) > max_len[1] and len(str(sales.name)) or max_len[1]
            max_len[2]=len(str(grouped_data[sales]['wholesale']['amt_on_whs'])) > max_len[2] and len(str(grouped_data[sales]['wholesale']['amt_on_whs'])) or max_len[2]
            max_len[3]=len(str(grouped_data[sales]['wholesale']['comm_on_whs'])) > max_len[3] and len(str(grouped_data[sales]['wholesale']['comm_on_whs'])) or max_len[3]
            max_len[4]=len(str(grouped_data[sales]['retail']['amt_on_ret'])) > max_len[4] and len(str(grouped_data[sales]['retail']['amt_on_ret'])) or max_len[4]
            max_len[5]=len(str(grouped_data[sales]['retail']['comm_on_ret'])) > max_len[5] and len(str(grouped_data[sales]['retail']['comm_on_ret'])) or max_len[5]
            max_len[6]=len(str(grouped_data[sales]['wholesale']['amt_of_whs'])) > max_len[6] and len(str(grouped_data[sales]['wholesale']['amt_of_whs'])) or max_len[6]
            max_len[7]=len(str(grouped_data[sales]['wholesale']['comm_of_whs'])) > max_len[7] and len(str(grouped_data[sales]['wholesale']['comm_of_whs'])) or max_len[7]
            max_len[8]=len(str(grouped_data[sales]['retail']['amt_of_ret'])) > max_len[8] and len(str(grouped_data[sales]['retail']['amt_of_ret'])) or max_len[8]
            max_len[9]=len(str(grouped_data[sales]['retail']['comm_of_ret'])) > max_len[9] and len(str(grouped_data[sales]['retail']['comm_of_ret'])) or max_len[9]
       
            no+=1
            row+=1
            
            
        for x in range(0,10):
            ws.col(x).width=max_len[x]*256
        
    
        
        
laporan_comm_summary_xls('report.laporan.comm.summary.xls', 'commission.compute.line.detail', parser=laporan_comm_summary_xls_parser)
            
            
            
            
            
            
            
        
        