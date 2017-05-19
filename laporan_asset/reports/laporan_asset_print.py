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


class laporan_asset_xls_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(laporan_asset_xls_parser, self).__init__(cr, uid, name,
                                                         context=context)
        self.context = context


class laporan_asset_xls(report_xls):
    
    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(laporan_asset_xls, self).__init__(
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
        
        
        
        
        ws = wb.add_sheet("Laporan Asset")
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        ws.preview_magn = 100
        ws.normal_magn = 100
        ws.print_scaling = 100
        ws.page_preview = False
        ws.set_fit_width_to_pages(1)
        
        ws.write_merge(0,0,0,14,"LAPORAN ASSET",title_style_center)
                    
        ws.write_merge(3,3,0,1,"Tanggal",normal_bold_style_a)
        ws.write_merge(3,3,2,4,": "+data['start_date']+" - "+data['end_date'],normal_bold_style_a)     
       
       
            
        col = 0
        
        row=5
        max_len = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        
        row+=1
        ws.write_merge(row,row+2,col,col+2,"Description",bold_border_all)
        
        headers = ["Journal Date","Age(Year)","Umur Asset dlm Bulan","Qty","Price/Unit","Total Price","Depr Per Month","X Penyusutan Up to Date Accounting","X Penyusutan Up to Date Theoritical","Total Akun Penyusutan","Outstanding X Penyusutan","Net Book Value","End of Depre Asset"]

        col = 3
        no=1
        for head in headers:
            ws.write_merge(row,row+2,col,col,head,bold_border_all)
            col+=1
            
        row+=3
        
        for rec in objects:
            
            
            ws.write(row,3,rec.date,normal_style)
            ws.write(row,4,rec.category_id.method_number/12,normal_style_float_round)
            ws.write(row,5,rec.category_id.method_number,normal_style_float_round)

                           #ini belum ambil datanya
            
            
            
            depr=rec.depreciation_line_ids and rec.depreciation_line_ids[0]
            if depr:
                upto_depr = self.pool.get('account.asset.depreciation.line').search(self.cr,self.uid,[('asset_id','=',rec.id),('move_check','=',True)])
                theo_depr = self.pool.get('account.asset.depreciation.line').search(self.cr,self.uid,[('asset_id','=',rec.id),('depreciation_date','<=',data['end_date'])])
                netbook_value = rec.value-rec.salvage_value

                end_date = datetime.strptime(data['end_date'],'%Y-%m-%d')

                for line in rec.depreciation_line_ids:
                    dep_date = datetime.strptime(line.depreciation_date,'%Y-%m-%d')
                    if dep_date<=end_date and line.move_check == True:
                        netbook_value = line.remaining_value
                    else:
                        break



                ws.write(row,9,depr.amount,normal_style_float)
                ws.write(row,10,len(upto_depr),normal_style_float_round)
                ws.write(row,11,len(theo_depr),normal_style_float_round)
                ws.write(row,12,depr.amount*len(upto_depr),normal_style_float_round)
                ws.write(row,13,(rec.category_id.method_number-len(upto_depr)),normal_style_float_round)
                ws.write(row,14,netbook_value,normal_style_float_round)

                max_len[9]=len(str(depr.amount)) > max_len[9] and len(str(depr.amount)) or max_len[9]
                max_len[10]=len(str(len(upto_depr))) > max_len[10] and len(str(len(upto_depr))) or max_len[10]
                max_len[11]=len(str(len(theo_depr))) > max_len[11] and len(str(len(theo_depr))) or max_len[11]
                max_len[12]=len(str(depr.amount*len(upto_depr))) > max_len[12] and len(str(depr.amount*len(upto_depr))) or max_len[12]
                max_len[13]=len(str(no)) > max_len[13] and len(str(no)) or max_len[13]
                max_len[14]=len(str(no)) > max_len[14] and len(str(no)) or max_len[14]
             
            for inv in rec.invoice_id:
                ws.write(row,15,inv.date_due,normal_style)
                max_len[15]=len(str(inv.date_due)) > max_len[15] and len(str(inv.date_due)) or max_len[15]
                for data in inv.invoice_line_ids:
                    if data.name==rec.name:
                        ws.write_merge(row,row,0,2,data.name,normal_style)
                        ws.write(row,6,data.quantity,normal_style_float)
                        ws.write(row,7,data.price_unit,normal_style_float)
                        ws.write(row,8,data.quantity*data.price_unit,normal_style_float)
                        
                        max_len[6]=len(str(data.quantity))+3 > max_len[6] and len(str(data.quantity))+3 or max_len[6]
                        max_len[7]=len(str(data.price_unit))+3 > max_len[7] and len(str(data.price_unit))+3 or max_len[7]
                        max_len[8]=len(str(data.quantity*data.price_unit))+3 > max_len[8] and len(str(data.quantity*data.price_unit))+3 or max_len[8]
                        
                        
                    else:
                        continue           
                    
            
                
                
                
               
            max_len[0]=len(str(rec.date)) > max_len[0] and len(str(rec.date)) or max_len[0]
            max_len[1]=len(str(rec.date)) > max_len[1] and len(str(rec.date)) or max_len[1]
            max_len[2]=len(str(rec.date)) > max_len[2] and len(str(rec.date)) or max_len[2]
            max_len[3]=len(str(rec.date)) > max_len[3] and len(str(rec.date)) or max_len[3]
            max_len[4]=len(str(rec.category_id.method_number))+3 > max_len[4] and len(str(rec.category_id.method_number))+3 or max_len[4]
            max_len[5]=len(str(rec.category_id.method_number))+3 > max_len[5] and len(str(rec.category_id.method_number))+3 or max_len[5] 
            
           
            
            
            
                
            no+=1
            row+=1
        for x in range(0,16):
            ws.col(x).width=max_len[x]*256
                
            
        
        
laporan_asset_xls('report.laporan.asset.xls', 'account.asset.asset', parser=laporan_asset_xls_parser)
            
            
            
            
            
            
            
        
        