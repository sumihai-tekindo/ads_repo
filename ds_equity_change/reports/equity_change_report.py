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


class equity_change_xls_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(equity_change_xls_parser, self).__init__(cr, uid, name,
                                                         context=context)
        self.context = context
        self.localcontext.update({
            'datetime': datetime,
            'get_modal_awal':self._get_modal_awal,
            'get_profit_loss':self._get_profit_loss,
            'get_prive':self._get_prive,
        })

    def _get_modal_awal(self,partner_id,company_id,date_start):
        cr = self.cr
        uid = self.uid

        ava_ids = self.pool.get("equity.available").search(cr,uid,[('company_id','=',company_id),('name','=',partner_id)])
        avas = self.pool.get("equity.available").browse(cr,uid,ava_ids)
        accounts = []
        accounts += [ava.equity_account_id.id for ava in avas]
        accounts += [ava.prive_account.id for ava in avas]
        query = """SELECT SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance
            from account_move_line aml
            left join account_account aa on aml.account_id=aa.id 
            where aml.date < '%s' and aml.account_id in %s

        """%(date_start,tuple(accounts))

        cr.execute(query)
        res = cr.fetchall()
        print "xxxxx1xxxxxx",res
        return res

    def _get_profit_loss(self,partner_id,date_start,date_end):
        ava_ids = self.pool.get("equity.available").search(cr,uid,[('company_id','=',company_id),('name','=',partner_id)])
        avas = self.pool.get("equity.available").browse(cr,uid,ava_ids)
        accounts = []
        accounts += [ava.pl_account_id.id for ava in avas]
        query = """SELECT SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance
            from account_move_line aml
            left join account_account aa on aml.account_id=aa.id 
            where aml.partner_id=%s and aml.date >= '%s' and aml.date <= '%s' and aml.account_id in %s

        """%(partner_id,date_start,date_end,tuple(accounts))
        cr.execute(query)
        res = cr.fetchall()
        print "xxxxxx2xxxxx",res
        return res

    def _get_prive(self,partner_id,date_start,date_end):
        ava_ids = self.pool.get("equity.available").search(cr,uid,[('company_id','=',company_id),('name','=',partner_id)])
        avas = self.pool.get("equity.available").browse(cr,uid,ava_ids)
        accounts = []
        accounts += [ava.prive_account.id for ava in avas]
        query = """SELECT SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance
            from account_move_line aml
            left join account_account aa on aml.account_id=aa.id 
            where aml.date >= '%s' and aml.date <= '%s' and aml.account_id in %s

        """%(date_start,date_end,tuple(accounts))
        cr.execute(query)
        res = cr.fetchall()
        print "xxxxx3xxxxxx",res
        return res
        

class equity_change_xls(report_xls):
    
    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(equity_change_xls, self).__init__(
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
        

        
        ws = wb.add_sheet("Equity Change Statement")
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        ws.preview_magn = 100
        ws.normal_magn = 100
        ws.print_scaling=100
        ws.page_preview = False
        ws.set_fit_width_to_pages(1)
        
        ws.write_merge(0,0,0,4,"EQUITY CHANGE STATEMENT",title_style_center)
        ws.write_merge(3,3,0,1,"PERIODE",normal_bold_style_a)
        ws.write_merge(3,3,2,4,": "+data['date_start']+" - "+data['date_end'],normal_bold_style_a)
       
        headers = ["Deskripsi","Debit","Credit"]
                   
        col = 0
        for head in headers:
            ws.write(5,col,head,normal_bold_style_b)
            col+=1
            
        no=1
        col = 0
        row=6
        max_len = [int(len(x)*1.5) for x in headers]



        for rec in objects:
            try:
                modal_awal = _p.get_modal_awal(rec.name.id,rec.company_id.id,data['date_start'])[0][2]
            except:
                modal_awal = 0.0

            modal_awal_d = modal_awal>0 and modal_awal or ""
            modal_awal_c = modal_awal<0 and abs(modal_awal) or ""

            try:
                pl_amount = _p.get_profit_loss(rec.name.id,data['date_start'],data['date_end'])[0][2]
            except:
                pl_amount = 0.0
            pl_d = pl_amount > 0 and pl_amount or ""
            pl_c = pl_amount < 0 and abs(pl_amount) or ""
            profitorloss = pl_d and "Loss" or "Profit"
            
            try:
                prive_amount = _p.get_prive(rec.name.id,data['date_start'],data['date_end'])[0][2]
            except:
                prive_amount = 0.0
            prive_d = prive_amount>0 and prive_amount or ""
            prive_c = prive_amount<0 and abs(prive_amount) or ""

            modal_akhir = (modal_awal + pl_amount) + prive_amount 
            modal_akhir_d = modal_akhir >0 and modal_akhir or ""
            modal_akhir_c = modal_akhir <0 and abs(modal_akhir) or ""

            print "==================",rec.name.name,modal_awal,pl_amount,prive_amount,modal_akhir

            ws.write(row,0,"Modal Awal %s"%(rec.name.name),normal_style)
            ws.write(row,1,"%s"%(modal_awal_d),normal_style_float_round)
            ws.write(row,2,"%s"%(modal_awal_c),normal_style_float_round)
            row+=1
            ws.write(row,0,"%s"%(profitorloss),normal_style)
            ws.write(row,1,"%s"%(pl_d),normal_style_float_round)
            ws.write(row,2,"%s"%(pl_c),normal_style_float_round)
            row+=1
            ws.write(row,0,"Prive %s"%(rec.name.name),normal_style)
            ws.write(row,1,"%s"%(prive_d),normal_style_float_round)
            ws.write(row,2,"%s"%(prive_c),normal_style_float_round)
            row+=1
            ws.write(row,0,"Modal Akhir %s"%(rec.name.name),normal_style)
            ws.write(row,1,"%s"%(prive_d),normal_style_float_round)
            ws.write(row,2,"%s"%(prive_c),normal_style_float_round)
            row+=2
            
            # max_len[0]=len(str(no))+3 > max_len[0] and len(str(no))+3 or max_len[0]
            # max_len[1]=len(str(rec.name)) > max_len[1] and len(str(rec.name)) or max_len[1]
            # max_len[2]=len(str(invoices[rec]['wholesale'])) > max_len[2] and len(str(invoices[rec]['wholesale'])) or max_len[2]
            
            
            row+=1
            no+=1
            
        # for x in range(0,5):
        #     ws.col(x).width=max_len[x]*256
            
        
        
equity_change_xls('report.equity.change.xls', 'equity.available', parser=equity_change_xls_parser)
            
        