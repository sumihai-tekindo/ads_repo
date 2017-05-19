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


class cashback_report_xls_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(cashback_report_xls_parser, self).__init__(cr, uid, name,
                                                         context=context)
        self.context = context

        
class cashback_report_xls(report_xls):
    
    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(cashback_report_xls, self).__init__(
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
        

        
        ws = wb.add_sheet("Payslip")
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        ws.preview_magn = 100
        ws.normal_magn = 100
        ws.print_scaling=100
        ws.page_preview = False
        ws.set_fit_width_to_pages(1)
        
        ws.write_merge(0,0,0,10,"REKAPITULASI CASHBACK CUSTOMER",title_style_center)
        ws.write_merge(3,3,0,1,"PERIODE",normal_bold_style_a)
        ws.write_merge(3,3,2,5,": "+data['start_date']+" - "+data['end_date'],normal_bold_style_a)
       
        headers = ["NO","Customer","Current Disc.","Omzet B.Disc.","Omzet A.Disc.","Omzet Paid","Deposit","Proposed Disc.","Cashback Amount","Force Rule","CB. Invoice"]
        col = 0
        for head in headers:
            ws.write(5,col,head,normal_bold_style_b)
            col+=1
        col = 0
        row=6
        no=1
        max_len = [0,0,0,0,0,0,0,0,0,0,0]
        for rec in objects:
            ws.write(row,0,no,normal_style_float_round)
            ws.write(row,1,rec.name.name,normal_style)
            ws.write(row,2,rec.current_disc,normal_style_float)
            ws.write(row,3,rec.omzet_before_disc,normal_style_float)
            ws.write(row,4,rec.omzet_after_disc,normal_style_float)
            ws.write(row,5,rec.omzet_paid,normal_style_float)
            ws.write(row,6,rec.deposit,normal_style_float)
            ws.write(row,7,rec.proposed_disc,normal_style_float)
            ws.write(row,8,rec.cash_back_amt,normal_style_float)
            ws.write(row,9,rec.force_cb,normal_style)
            ws.write(row,10,rec.invoice_id.number,normal_style)
            
            max_len[0]=len(str(no))+3 > max_len[0] and len(str(no))+3 or max_len[0]
            max_len[1]=len(str(rec.name.name)) > max_len[1] and len(str(rec.name.name)) or max_len[1]
            max_len[2]=len(str(rec.current_disc))+3 > max_len[2] and len(str(rec.current_disc))+3 or max_len[2]
            max_len[3]=len(str(rec.omzet_before_disc)) > max_len[3] and len(str(rec.omzet_before_disc)) or max_len[3]
            max_len[4]=len(str(rec.omzet_after_disc)) > max_len[4] and len(str(rec.omzet_after_disc)) or max_len[4]
            max_len[5]=len(str(rec.omzet_paid)) > max_len[5] and len(str(rec.omzet_paid)) or max_len[5]
            max_len[6]=len(str(rec.deposit))+3 > max_len[6] and len(str(rec.deposit))+3 or max_len[6]
            max_len[7]=len(str(rec.proposed_disc))+3 > max_len[7] and len(str(rec.proposed_disc))+3 or max_len[7]
            max_len[8]=len(str(rec.cash_back_amt)) > max_len[8] and len(str(rec.cash_back_amt)) or max_len[8]
            max_len[9]=len(str(rec.force_cb)) > max_len[9] and len(str(rec.force_cb)) or max_len[9]
            max_len[10]=len(str(rec.invoice_id.number)) > max_len[10] and len(str(rec.invoice_id.number)) or max_len[10]
            no+=1
            row+=1
        
        for x in range(0,11):
            ws.col(x).width=max_len[x]*256 
        ws.write(row+1,1,"TOTAL",title_style)
        ws.write(row+1,3,xlwt.Formula("SUM($D$6:$D$"+str(row)+")"),subtotal_style2)
        ws.write(row+1,4,xlwt.Formula("SUM($E$6:$E$"+str(row)+")"),subtotal_style2)
        ws.write(row+1,5,xlwt.Formula("SUM($F$6:$F$"+str(row)+")"),subtotal_style2)
        ws.write(row+1,8,xlwt.Formula("SUM($I$6:$I$"+str(row)+")"),subtotal_style2)
cashback_report_xls('report.cashback.report.xls', 'account.cashback.line',
                    parser=cashback_report_xls_parser)