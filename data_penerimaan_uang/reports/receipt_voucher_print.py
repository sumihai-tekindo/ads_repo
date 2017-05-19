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


class receipt_voucher_xls_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(receipt_voucher_xls_parser, self).__init__(cr, uid, name,
                                                         context=context)
        self.context = context


class receipt_voucher_xls(report_xls):
    
    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(receipt_voucher_xls, self).__init__(
            name, table, rml, parser, header, store)


    def generate_xls_report(self, _p, _xs, data, objects, wb):
        
        grouping = {}
        for rec in objects:
            if rec.journal_id in grouping.keys():
                dummy = grouping.get(rec.journal_id,[])
                dummy.append(rec)
                grouping.update({rec.journal_id:dummy})
            else:
                grouping.update({rec.journal_id:[]})
        
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
        
        border_all = xlwt.easyxf('border:top thick, bottom thick, left thick, right thick')
        bold_border_all = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick, bottom thick, left thick, right thick')
        

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
            
            ws.write_merge(0,0,0,2,"RECEIPT VOUCHER",title_style_center)
            
            ws.write_merge(3,3,0,1,"No Voucher", normal_bold_style)
            ws.write_merge(3,3,2,4,": " ,normal_bold_style_a)             
            ws.write_merge(4,4,0,1,"Tanggal",normal_bold_style_a)
            ws.write_merge(4,4,2,4,": "+data['start_date']+" - "+data['end_date'],normal_bold_style_a)     #ini belum selesai
            ws.write_merge(5,5,0,1,"Kas/Bank",normal_bold_style_a)
            ws.write_merge(5,5,2,4,": ",normal_bold_style_a)
           
           
                
            col = 0
            row=8
            max_len = [0,0,0]
            
            
            headers = ["No","Keterangan","Total"]
            ws.write_merge(row,row,0,4,group.name)
            row+=1
            col = 0
            no=1
            for head in headers:
                ws.write(row,col,head,normal_bold_style_b)
                col+=1
            row+=1
            for rec in grouping.get(group,[]):    
                ws.write(row,0,no,normal_style_float_round)
                ws.write(row,1,rec.name,normal_style)
                ws.write(row,2,rec.credit,normal_style_float)
                
                max_len[0]=len(str(no))+3 > max_len[0] and len(str(no))+3 or max_len[0]
                max_len[1]=len(str(rec.name)) > max_len[1] and len(str(rec.name)) or max_len[1]
                max_len[2]=len(str(rec.credit)) > max_len[2] and len(str(rec.credit)) or max_len[2]
                
                no+=1
                row+=1
            for x in range(0,3):
                ws.col(x).width=max_len[x]*256
                
            ws.write(row+1,1,"TOTAL",title_style)
            #SUM('BCA 270.302.7211'!B9:B103)
            ws.write(row+1,2,xlwt.Formula("SUM('"+group.name+"'!$C$11:$C$"+str(row)+")"),subtotal_style2)
            
            row+=4
        
        
            ws.write_merge(row,row,0,1,"Dibuat",bold_border_all)
            ws.write_merge(row,row,2,5,"Diperiksa",bold_border_all)
            ws.write_merge(row,row,6,7,"Diketahui",bold_border_all)
            
            row+=1
            
            ws.write_merge(row,row+2,0,1,"",border_all)
            ws.write_merge(row,row+2,2,3,"",border_all)
            ws.write_merge(row,row+2,4,5,"",border_all)
            ws.write_merge(row,row+2,6,7,"",border_all)
        
        
receipt_voucher_xls('report.receipt.voucher.xls', 'account.move.line', parser=receipt_voucher_xls_parser)
            
            
            
            
            
            
            
        