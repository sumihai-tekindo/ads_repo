import xlwt
from xlwt import Formula as fm
from datetime import datetime
from openerp.osv import orm
from openerp.addons.report_xls.report_xls import report_xls
# from openerp.addons.report_xls.utils import rowcol_to_cell, _render

import time
from openerp.exceptions import Warning
from openerp.report import report_sxw
from openerp.tools.translate import translate
import logging

# from .nov_account_journal import nov_journal_print
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class laporan_ar_xls_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(laporan_ar_xls_parser, self).__init__(cr, uid, name,
                                                         context=context)
        self.context = context


class laporan_ar_xls(report_xls):
    
    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(laporan_ar_xls, self).__init__(
            name, table, rml, parser, header, store)



    
    

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        ##Penempatan untuk template rows
        
        grouping = {}
        for group in objects:
            if group.partner_id in grouping.keys():
                dummy = grouping.get(group.partner_id,[])
                dummy.append(group)
                grouping.update({group.partner_id:dummy})
            else:
                grouping.update({group.partner_id:[group]})
        
        
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
        
        border_all                      = xlwt.easyxf('border:top thick, bottom thick, left thick, right thick')
        bold_border_all                 = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz center;pattern: pattern solid, fore_color gray25; border:top thin, bottom thin, left thin, right thin')
        

        if not grouping:
            raise Warning(_('Record\'s not found  between Start Date: %s and End Date: %s. ') % (data['start_date'], data['end_date']))
        for group in grouping.keys():
            ws = wb.add_sheet(group.name)
            ws.panes_frozen = True
            ws.remove_splits = True
            ws.portrait = 0  # Landscape
            ws.fit_width_to_pages = 1
            ws.preview_magn = 100
            ws.normal_magn = 100
            ws.print_scaling=100
            ws.page_preview = False
            ws.set_fit_width_to_pages(1)
            
            ws.write_merge(0,0,0,4,"AR PER CUSTOMER",title_style_center)
            ws.write_merge(3,3,0,1,"PERIODE",normal_bold_style_a)
            ws.write_merge(3,3,2,4,": "+data['start_date']+" - "+data['end_date'],normal_bold_style_a)
           
           
            col = 0
            row=6
            max_len = [0,0,0,0,0,0,0,0]
           
           
            headers1 = ["No","No Invoice","Tanggal Invoice","Nilai Invoice"]
            headers2 = ["Payment"]
            headers3 = ["Tanggal Payment","Nilai Payment"]
            headers4 = ["Outstanding","Due Date"]
            row+=1
            col = 0
            
            
            
            for head1 in headers1:
                ws.write_merge(row,row+1,col,col,head1,bold_border_all)
                col+=1
                       
            col = 4
            for head2 in headers2:
                ws.write_merge(row,row,col,col+1,head2,bold_border_all)
                col+=1
                
            col = 4    
            for head3 in headers3:
                ws.write_merge(row+1,row+1,col,col,head3,bold_border_all)
                col+=1
                
            col = 6    
            for head4 in headers4:
                ws.write_merge(row,row+1,col,col,head4,bold_border_all)
                col+=1
            
            row+=2
            no=1
            
            for o in grouping.get(group,[]):
                         
                ws.write(row,0,no,normal_style_float_round)
                ws.write(row,1,o.number,normal_style)
                ws.write(row,2,o.date_invoice,normal_style)
                ws.write(row,3,o.amount_total,normal_style_float)                
                ws.write(row,6,o.residual,normal_style_float)
                ws.write(row,7,o.date_due,normal_style)
                 
                for pay in o.payment_move_line_ids:
                    ws.write(row,4,pay.date,normal_style)
                    ws.write(row,5,pay.debit,normal_style_float)
                    max_len[4]=len(str(pay.date)) > max_len[4] and len(str(pay.date)) or max_len[4]
                    max_len[5]=len(str(pay.debit))+5 > max_len[5] and len(str(pay.debit))+5 or max_len[5]
                    row+=1
                    
                max_len[0]=len(str(no))+3 > max_len[0] and len(str(no))+3 or max_len[0]
                max_len[1]=len(str(o.number)) > max_len[1] and len(str(o.number)) or max_len[1]
                max_len[2]=len(str(o.date_invoice)) > max_len[2] and len(str(o.date_invoice)) or max_len[2]
                max_len[3]=len(str(o.amount_total))+5 > max_len[3] and len(str(o.amount_total))+5 or max_len[3]
                
                max_len[6]=len(str(o.residual))+5 > max_len[6] and len(str(o.residual))+5 or max_len[6]
                max_len[7]=len(str(o.date_due)) > max_len[7] and len(str(o.date_due)) or max_len[7]
                 
                row+=1
                no+=1
                
            for x in range(0,8):
                ws.col(x).width=max_len[x]*256
                
            ws.write(row,1,"TOTAL",title_style)
            ws.write(row,3,xlwt.Formula("SUM($D$7:$D$"+str(row)+")"),subtotal_style2)
            ws.write(row,5,xlwt.Formula("SUM($F$7:$F$"+str(row)+")"),subtotal_style2)
            ws.write(row,6,xlwt.Formula("SUM($G$7:$G$"+str(row)+")"),subtotal_style2)
        
laporan_ar_xls('report.laporan.ar.xls', 'account.invoice', parser=laporan_ar_xls_parser)
            
        