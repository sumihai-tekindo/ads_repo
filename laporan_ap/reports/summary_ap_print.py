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


class summary_ap_xls_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(summary_ap_xls_parser, self).__init__(cr, uid, name,
                                                         context=context)
        self.context = context


class summary_ap_xls(report_xls):
    
    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(summary_ap_xls, self).__init__(
            name, table, rml, parser, header, store)


    def generate_xls_report(self, _p, _xs, data, objects, wb):
        
        dummy_total={}
        for o in objects:
            if o.partner_id in dummy_total.keys():
                total = dummy_total.get(o.partner_id).get('total',0.0)
                total+= o.amount_total
                payment = dummy_total.get(o.partner_id).get('payment',0.0)
                payment+=o.amount_total-o.residual
                residual = dummy_total.get(o.partner_id).get('residual',0.0)
                residual +=o.residual
                dummy_total.update({o.partner_id:
                                        {'total':total,
                                         'payment':payment,
                                         'residual':residual}
                                    })
            
            else:
                dummy_total.update({o.partner_id:
                                            {'total':o.amount_total,
                                             'payment':o.amount_total-o.residual,
                                             'residual':o.residual}
                                    })
        
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
        
        border_all                      = xlwt.easyxf('border:top thick, bottom thick, left thick, right thick')
        bold_border_all                 = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz center;pattern: pattern solid, fore_color gray25; border:top thin, bottom thin, left thin, right thin')
        
        
        
        ws = wb.add_sheet("Summary AP")
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        ws.preview_magn = 100
        ws.normal_magn = 100
        ws.print_scaling=100
        ws.page_preview = False
        ws.set_fit_width_to_pages(1)
        
        ws.write_merge(0,0,0,4,"SUMMARY AP",title_style_center)
        ws.write_merge(3,3,0,1,"PERIODE",normal_bold_style_a)
        ws.write_merge(3,3,2,4,": "+data['start_date']+" - "+data['end_date'],normal_bold_style_a)
       
       
        col = 0
        row=6
        max_len = [0,0,0,0,0]
       
       
        headers = ["No","Nama Vendor","Total Invoice","Payment","Outstanding"]
        
        row+=1
        col = 0
        
        
        for head in headers:
            ws.write(row,col,head,bold_border_all)
            col+=1
        
        
        row+=1
        no=1
        
        
        
        
        
        for rec in dummy_total:
            
            total_invoice = dummy_total.get(rec,0.0).get('total',0.0)
            total_payment = dummy_total.get(rec,0.0).get('payment',0.0)
            residual = dummy_total.get(rec,0.0).get('residual',0.0)
            
            
            ws.write(row,0,no,normal_style_float_round)
            ws.write(row,1,rec.name,normal_style)
            ws.write(row,2,total_invoice,normal_style)                ##################
            ws.write(row,3,total_payment,normal_style)
            ws.write(row,4,residual,normal_style)
            
            
            max_len[0]=len(str(no))+2 > max_len[0] and len(str(no))+2 or max_len[0]
            max_len[1]=len(str(rec.name)) > max_len[1] and len(str(rec.name)) or max_len[1]
            max_len[2]=len(str(total_invoice))+5 > max_len[2] and len(str(total_invoice))+5 or max_len[2]
            max_len[3]=len(str(total_payment))+5 > max_len[3] and len(str(total_payment))+5 or max_len[3]
            max_len[4]=len(str(residual))+5 > max_len[4] and len(str(residual))+5 or max_len[4]
            
            row+=1
            no+=1
        for x in range(0,5):
            ws.col(x).width=max_len[x]*256
            
        
        
summary_ap_xls('report.summary.ap.xls', 'account.invoice', parser=summary_ap_xls_parser)
            
        