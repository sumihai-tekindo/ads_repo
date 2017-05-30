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


class laporan_comm_offline_xls_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(laporan_comm_offline_xls_parser, self).__init__(cr, uid, name,
                                                         context=context)
        self.context = context
        self.localcontext.update({
            'datetime': datetime,
            'group_data':self._group_data
        })


    def _group_data(self,objects):
        commissions = {}
        print "==========1============",objects
        for comm in objects:
            rule_type = (comm.rule_type=='whs_off' and 'wholesale') or (comm.rule_type=='ret_off' and 'retail') or False
            amt_whs = comm.rule_type=='whs_off' and comm.amount_untaxed or 0.0
            comm_whs = comm.rule_type=='whs_off' and comm.commission_amount or 0.0
            amt_ret = comm.rule_type=='ret_off' and comm.amount_untaxed or 0.0 
            comm_ret = comm.rule_type=='ret_off' and comm.commission_amount or 0.0
            if rule_type:
                if comm.sale_user_id not in commissions:
                    commissions.update({comm.sale_user_id:{comm.partner_id:{'wholesale':{'amount':amt_whs,'commission':comm_whs},'retail':{'amount':amt_ret,'commission':comm_ret}}}})
                else:
                    if comm.partner_id not in commissions[comm.sale_user_id]:
                        commissions[comm.sale_user_id].update({comm.partner_id:{'wholesale':{'amount':amt_whs,'commission':comm_whs},'retail':{'amount':amt_ret,'commission':comm_ret}}})
                    else:
                        if rule_type not in commissions[comm.sale_user_id][comm.partner_id]:
                            commissions[comm.sale_user_id][comm.partner_id]['wholesale'].update({'amount':amt_whs,'commission':comm_whs})
                            commissions[comm.sale_user_id][comm.partner_id]['retail'].update({'amount':amt_ret,'commission':comm_ret})
                        else:
                            amt_whs+=commissions[comm.sale_user_id][comm.partner_id]['wholesale']['amount']
                            comm_whs+=commissions[comm.sale_user_id][comm.partner_id]['wholesale']['commission']
                            amt_ret+=commissions[comm.sale_user_id][comm.partner_id]['retail']['amount']
                            comm_ret+=commissions[comm.sale_user_id][comm.partner_id]['retail']['commission']
                            commissions[comm.sale_user_id][comm.partner_id]['wholesale'].update({'amount':amt_whs,'commission':comm_whs})
                            commissions[comm.sale_user_id][comm.partner_id]['retail'].update({'amount':amt_ret,'commission':comm_ret})
        return commissions

class laporan_comm_offline_xls(report_xls):
    
    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(laporan_comm_offline_xls, self).__init__(
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
        
        
        
        
        ws = wb.add_sheet("Komisi Offline")
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        ws.preview_magn = 100
        ws.normal_magn = 100
        ws.print_scaling=100
        ws.page_preview = False
        ws.set_fit_width_to_pages(1)
        
        ws.write_merge(0,0,0,6,"LAPORAN KOMISI OFFLINE",title_style_center)
                    
        ws.write_merge(3,3,0,1,"Tanggal",normal_bold_style_a)
        ws.write_merge(3,3,2,4,": "+data['start_date']+" - "+data['end_date'],normal_bold_style_a)     
       
           
            
        col = 0
        row=5
        
        
        headers = ["No","Sales Person","Customer","Penjualan Wholesale","Komisi Wholesale","Penjualan Retail","Komisi Retail"]
        max_len = [int(len(x)*1.5) for x in headers]
        row+=1
        col = 0
        no=1
        for head in headers:
            ws.write(row,col,head,bold_border_all)
            col+=1    
        row+=1
        grouped_data = _p.group_data(objects)

        formula1=""
        formula2=""
        formula3=""
        formula4=""
        for sales in grouped_data:  
            ws.write(row,0,no,normal_style_float_round)
            ws.write(row,1,sales.name,normal_style)
            start_row = row
            for cust in grouped_data[sales]:
                ws.write(row,2,cust.name,normal_style)
                ws.write(row,3,grouped_data[sales][cust]['wholesale']['amount'],normal_style_float)
                ws.write(row,4,grouped_data[sales][cust]['wholesale']['commission'],normal_style_float)
                ws.write(row,5,grouped_data[sales][cust]['retail']['amount'],normal_style_float)              
                ws.write(row,6,grouped_data[sales][cust]['retail']['commission'],normal_style_float)
                
                max_len[0]=len(str(no))+3 > max_len[0] and len(str(no))+3 or max_len[0]
                max_len[1]=len(str(sales.name)) > max_len[1] and len(str(sales.name)) or max_len[1]
                max_len[2]=len(str(cust.name)) > max_len[2] and len(str(cust.name)) or max_len[2]
                max_len[3]=len(str(grouped_data[sales][cust]['wholesale']['amount'])) > max_len[3] and len(str(grouped_data[sales][cust]['wholesale']['amount'])) or max_len[3]
                max_len[4]=len(str(grouped_data[sales][cust]['wholesale']['commission'])) > max_len[4] and len(str(grouped_data[sales][cust]['wholesale']['commission'])) or max_len[4]
                max_len[5]=len(str(grouped_data[sales][cust]['retail']['amount'])) > max_len[5] and len(str(grouped_data[sales][cust]['retail']['amount'])) or max_len[5]
                max_len[6]=len(str(grouped_data[sales][cust]['retail']['commission'])) > max_len[6] and len(str(grouped_data[sales][cust]['retail']['commission'])) or max_len[6]
           
                no+=1
                row+=1
            ws.write_merge(row,row,0,2,"TOTAL SALES %s"%sales.name,title_style)
            ws.write(row,3,xlwt.Formula("SUM($D$"+str(start_row+1)+":$D$"+str(row)+")"),subtotal_style2)
            ws.write(row,4,xlwt.Formula("SUM($E$"+str(start_row+1)+":$E$"+str(row)+")"),subtotal_style2)
            ws.write(row,5,xlwt.Formula("SUM($F$"+str(start_row+1)+":$F$"+str(row)+")"),subtotal_style2)
            ws.write(row,6,xlwt.Formula("SUM($G$"+str(start_row+1)+":$G$"+str(row)+")"),subtotal_style2)
            formula1+="+SUM($D$"+str(start_row+1)+":$D$"+str(row)+")"
            formula2+="+SUM($E$"+str(start_row+1)+":$E$"+str(row)+")"
            formula3+="+SUM($F$"+str(start_row+1)+":$F$"+str(row)+")"
            formula4+="+SUM($G$"+str(start_row+1)+":$G$"+str(row)+")"
            row+=2
        for x in range(0,7):
            ws.col(x).width=max_len[x]*256
        
        ws.write_merge(row,row,0,2,"GRAND TOTAL",title_style)
        ws.write(row,3,xlwt.Formula(formula1[1:]),subtotal_style2)
        ws.write(row,4,xlwt.Formula(formula2[1:]),subtotal_style2)
        ws.write(row,5,xlwt.Formula(formula3[1:]),subtotal_style2)
        ws.write(row,6,xlwt.Formula(formula4[1:]),subtotal_style2)
        
        
laporan_comm_offline_xls('report.laporan.comm.offline.xls', 'commission.compute.line.detail', parser=laporan_comm_offline_xls_parser)
            
            
            
            
            
            
            
        
        