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


class laporan_produk_xls_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(laporan_produk_xls_parser, self).__init__(cr, uid, name,
                                                         context=context)
        self.context = context


class laporan_produk_xls(report_xls):
    
    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(laporan_produk_xls, self).__init__(
            name, table, rml, parser, header, store)


    def generate_xls_report(self, _p, _xs, data, objects, wb):
       
        ############################################################################################################
        # get product sold
        ############################################################################################################
        dummy_sold = {}
        for mv in objects:
            if mv.product_id in dummy_sold.keys():
                x = dummy_sold.get(mv.product_id,False) and dummy_sold.get(mv.product_id).get('quantity',0.0)
                y = dummy_sold.get(mv.product_id,False) and dummy_sold.get(mv.product_id).get('price_unit',0.0)
                x+=mv.product_uom_qty
                y = (y+mv.price_unit)/2.0
                dummy_sold.update({mv.product_id:{'quantity':x,'price_unit':y}})
            else:
                dummy_sold.update({mv.product_id:{'quantity':mv.product_uom_qty,'price_unit':mv.price_unit}})
        products = self.pool.get('product.product').browse(self.cr,self.uid,data['product_ids'])
        product_ids = data['product_ids']
        #############################################################################################################
        # get product loss
        #############################################################################################################
        loc_1 = self.pool.get('stock.location').search(self.cr,self.uid,[('usage','=','internal')])
        loc_2 = self.pool.get('stock.location').search(self.cr,self.uid,[('usage','=','inventory')])
        location_stock_ids = [x.id for x in self.pool.get('stock.location').browse(self.cr,self.uid,loc_1)]
        location_loss_ids = [x.id for x in self.pool.get('stock.location').browse(self.cr,self.uid,loc_2)]
        mv_ids_pos = self.pool.get('stock.move').search(self.cr,self.uid,[('date','>=',data['start_date']),('date','<=',data['end_date']),('state','=','done'),
                                      ('product_id','in',product_ids),('location_id','in',location_loss_ids),('location_dest_id','in',location_stock_ids)
                                      ])
        mv_ids_neg = self.pool.get('stock.move').search(self.cr,self.uid,[('date','>=',data['start_date']),('date','<=',data['end_date']),('state','=','done'),
                                      ('product_id','in',product_ids),('location_id','in',location_stock_ids),('location_dest_id','in',location_loss_ids)
                                      ])
        dummy_loss = {}
        for mv in self.pool.get('stock.move').browse(self.cr,self.uid,mv_ids_pos):
            if mv.product_id in dummy_loss.keys():
                x = dummy_loss.get(mv.product_id,False) and dummy_loss.get(mv.product_id).get('quantity',0.0)
                y = dummy_loss.get(mv.product_id,False) and dummy_loss.get(mv.product_id).get('price_unit',0.0)
                z = dummy_loss.get(mv.product_id,False) and dummy_loss.get(mv.product_id).get('value',0.0)
                x+=mv.product_uom_qty
                y = mv.quant_ids and (y+(sum([x.cost for x in mv.quant_ids])/float(len(mv.quant_ids))))/2.0 or 0.0
                z += sum([x.inventory_value for x in mv.quant_ids])
                dummy_loss.update({mv.product_id:{'quantity':x,'price_unit':y,'value':z}})
            else:
                y=mv.quant_ids and sum([x.cost for x in mv.quant_ids])/float(len(mv.quant_ids)) or 0.0
                z=sum([x.inventory_value for x in mv.quant_ids])
                dummy_loss.update({mv.product_id:{'quantity':mv.product_uom_qty,'price_unit':y,'value':z}})

                
         
                
        for mv in self.pool.get('stock.move').browse(self.cr,self.uid,mv_ids_neg):
            if mv.product_id in dummy_loss.keys():
                x = (dummy_loss.get(mv.product_id,False) and dummy_loss.get(mv.product_id).get('quantity',0.0))
                y = (dummy_loss.get(mv.product_id,False) and dummy_loss.get(mv.product_id).get('price_unit',0.0))
                z = -1*(dummy_loss.get(mv.product_id,False) and dummy_loss.get(mv.product_id).get('value',0.0))
                x += -1*mv.product_uom_qty
                y = mv.quant_ids and (y+(sum([x.cost for x in mv.quant_ids])/float(len(mv.quant_ids))))/2.0 or 0.0
                z += -1*sum([x.inventory_value for x in mv.quant_ids])
                dummy_loss.update({mv.product_id:{'quantity':x,'price_unit':y,'value':z}})
            else:
                x = -1*mv.product_uom_qty
                y = (mv.quant_ids and sum([x.cost for x in mv.quant_ids])/float(len(mv.quant_ids))) or 0.0
                z = -1*(sum([x.inventory_value for x in mv.quant_ids]))
                dummy_loss.update({mv.product_id:{'quantity':x,'price_unit':y,'value':z}})
                
        
        products = self.pool.get('product.product').browse(self.cr,self.uid,data['product_ids'])
        
        ############################################################################################################
        # get product purchased
        ############################################################################################################
        location_stock = self.pool.get('stock.location').search(self.cr,self.uid,[('usage','=','internal')])
        location_supplier = self.pool.get('stock.location').search(self.cr,self.uid,[('usage','=','supplier')])
        loc_stock = [x.id for x in self.pool.get('stock.location').browse(self.cr,self.uid,location_stock)]
        loc_suppl = [x.id for x in self.pool.get('stock.location').browse(self.cr,self.uid,location_supplier)]
        mv_ids_bought = self.pool.get('stock.move').search(self.cr,self.uid,[('date','>=',data['start_date']),('date','<=',data['end_date']),('state','=','done'),
                                      ('product_id','in',product_ids),('location_id','in',location_supplier),('location_dest_id','in',location_stock)
                                      ])
        dummy_bought = {}
        for mv in self.pool.get('stock.move').browse(self.cr,self.uid,mv_ids_bought):
            if mv.product_id in dummy_bought.keys():
                x = dummy_bought.get(mv.product_id,False) and dummy_bought.get(mv.product_id).get('quantity',0.0)
                y = dummy_bought.get(mv.product_id,False) and dummy_bought.get(mv.product_id).get('price_unit',0.0)
                z = dummy_bought.get(mv.product_id,False) and dummy_bought.get(mv.product_id).get('value',0.0)
                x+=mv.product_uom_qty
                y = mv.quant_ids and (y+(sum([x.cost for x in mv.quant_ids])/float(len(mv.quant_ids))))/2.0 or 0.0
                
                z += sum([x.inventory_value for x in mv.quant_ids])
                dummy_bought.update({mv.product_id:{'quantity':x,'price_unit':y,'value':z}})
            else:
                y=mv.quant_ids and sum([x.cost for x in mv.quant_ids])/float(len(mv.quant_ids)) or 0.0
                z=sum([x.inventory_value for x in mv.quant_ids])
                dummy_bought.update({mv.product_id:{'quantity':mv.product_uom_qty,'price_unit':y,'value':z}})
                
        
        products = self.pool.get('product.product').browse(self.cr,self.uid,data['product_ids'])
        
        
        #############################################################################################################
        # get initial stock
        #############################################################################################################
        context1 = {}
        context1['history_date'] = data['start_date']
        context1['search_default_group_by_product'] = True
        context1['search_default_group_by_location'] = True
        stock_awal_ids = self.pool.get('stock.history').search(self.cr,self.uid,[('product_id','in',data['product_ids']),('date','<=',data['start_date'])],context=context1)
        
        if stock_awal_ids:
            stock_awal_data = self.pool.get('stock.history').browse(self.cr,self.uid,stock_awal_ids,context=context1)
        else:
            stock_awal_data = {}
        print "=============stock_awal_data=============",stock_awal_data
        prod = {}
        for p in products:
            prod.update({p.id:p})
        dummy_stock_awal = {}
        for mv in stock_awal_data:
            if mv in dummy_stock_awal.keys():
                x = dummy_stock_awal.get(mv.product_id).get('quantity',0.0)
                x += mv.quantity 
                y = dummy_stock_awal.get(mv.product_id).get('price_unit',0.0)
                y = (y+mv.price_unit_on_quant)/2.0 
                z = dummy_stock_awal.get(mv.product_id).get('price_unit',0.0)
                z +=mv.inventory_value or 0.0
                dummy_stock_awal.update({mv.product_id:{'quantity':x,'price_unit':y,'value':z}})
            else:
                dummy_stock_awal.update({mv.product_id:{'quantity':mv.quantity,'price_unit':mv.price_unit_on_quant,'value':mv.inventory_value}})
        ############################################################################################################
        # get final stock
        ############################################################################################################
        context2 = {}
        context2['history_date'] = data['end_date']
        context2['search_default_group_by_product'] = True
        context2['search_default_group_by_location'] = True
        
        stock_akhir_ids = self.pool.get('stock.history').search(self.cr,self.uid,[('product_id','in',data['product_ids']),('date','<=',data['end_date'])],context=context2)
        stock_akhir_data = self.pool.get('stock.history').browse(self.cr,self.uid,stock_akhir_ids,context=context2)
        dummy_stock_akhir = {}
        for mv in stock_akhir_data:
            if mv in dummy_stock_akhir.keys():
                x = dummy_stock_akhir.get(mv.product_id).get('quantity',0.0)
                x += mv.quantity 
                y = dummy_stock_akhir.get(mv.product_id).get('price_unit',0.0)
                y = (y+mv.price_unit_on_quant)/2.0 
                z = dummy_stock_akhir.get(mv.product_id).get('price_unit',0.0)
                z +=mv.inventory_value or 0.0
                dummy_stock_akhir.update({mv.product_id:{'quantity':x,'price_unit':y,'value':z}})
            else:
                print "=====================",mv.price_unit_on_quant
                dummy_stock_akhir.update({mv.product_id:{'quantity':mv.quantity,'price_unit':mv.price_unit_on_quant,'value':mv.inventory_value}})
        ############################################################################################################
        keys = list(set(dummy_sold.keys()+dummy_stock_awal.keys()+dummy_stock_akhir.keys()))
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
        
        
        
        
        ws = wb.add_sheet("Laporan Produk")
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        ws.preview_magn = 100
        ws.normal_magn = 100
        ws.print_scaling=100
        ws.page_preview = False
        ws.set_fit_width_to_pages(1)
        
        ws.write_merge(0,0,0,14,"LAPORAN PRODUK",title_style_center)
                    
        ws.write_merge(3,3,0,1,"Tanggal",normal_bold_style_a)
        ws.write_merge(3,3,2,4,": "+data['start_date']+" - "+data['end_date'],normal_bold_style_a)     #ini belum selesai
        
       
           
            
        col = 0
        row=5
        max_len = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        
        
        headers1 = ["No","Nama Produk"]
        headers2 = ["Stock Awal","Pembelian","Penjualan","Hilang/Rusak","Saldo Akhir"]
        headers3 = ["Unit","Harga Satuan","Jumlah","Unit","Harga Satuan","Jumlah","Unit","Harga Satuan","Jumlah","Unit","Harga Satuan","Jumlah","Unit","Harga Satuan","Jumlah"]
        row+=1
        col = 0
        no=1
        for head1 in headers1:
            ws.write_merge(row,row+1,col,col,head1,bold_border_all)
            col+=1
            
        col = 2
        
        for head2 in headers2:
            ws.write_merge(row,row,col,col+2,head2,bold_border_all)
            col+=3
        
        row+=1
        col=2 
        
        for head3 in headers3:
            ws.write(row,col,head3,bold_border_all)
            col+=1
            
        row+=1
        
        for mv in keys:
         
            product = mv.name
            
            stock_bought = dummy_bought.get(mv,False) and dummy_bought.get(mv).get('quantity',0.0) or 0.0
            stock_bought_price = dummy_bought.get(mv,False) and dummy_bought.get(mv,0.0).get('price_unit',0.0) or 0.0
            stock_bought_value = dummy_bought.get(mv,False) and dummy_bought.get(mv).get('value',0.0) or 0.0
            
            stock_awal = dummy_stock_awal.get(mv,False) and dummy_stock_awal.get(mv).get('quantity',0.0) or 0.0
            stock_awal_price = dummy_stock_awal.get(mv,False) and dummy_stock_awal.get(mv,0.0).get('price_unit',0.0) or 0.0
            stock_awal_value = dummy_stock_awal.get(mv,False) and dummy_stock_awal.get(mv).get('value',0.0) or 0.0
            
            stock_sold = dummy_sold.get(mv,False) and dummy_sold.get(mv).get('quantity',0.0) or 0.0
            price_unit_sold = dummy_sold.get(mv,False) and dummy_sold.get(mv).get('price_unit',0.0) or 0.0
            
            stock_loss = dummy_loss.get(mv,False) and dummy_loss.get(mv).get('quantity',0.0) or 0.0
            price_unit_loss = dummy_loss.get(mv,False) and dummy_loss.get(mv).get('price_unit',0.0) or 0.0
            stock_loss_value = dummy_loss.get(mv,False) and dummy_loss.get(mv).get('value',0.0) or 0.0
            
            stock_akhir = dummy_stock_akhir.get(mv,False) and dummy_stock_akhir.get(mv).get('quantity',0.0) or 0.0
            stock_akhir_price = dummy_stock_akhir.get(mv,False) and dummy_stock_akhir.get(mv).get('price_unit',0.0) or 0.0
            stock_akhir_value = dummy_stock_akhir.get(mv,False) and dummy_stock_akhir.get(mv).get('value',0.0) or 0.0
            
            
            ws.write(row,0,no,normal_style_float_round)
            ws.write(row,1,product,normal_style)
            ws.write(row,2,stock_awal,normal_style_float)
            ws.write(row,3,stock_awal_price,normal_style_float)
            ws.write(row,4,stock_awal_value,normal_style_float)
            ws.write(row,5,stock_bought,normal_style_float)
            ws.write(row,6,stock_bought_price,normal_style_float)
            ws.write(row,7,stock_bought_value,normal_style_float)
            ws.write(row,8,stock_sold,normal_style_float)
            ws.write(row,9,price_unit_sold,normal_style_float)
            ws.write(row,10,stock_sold*price_unit_sold,normal_style_float)
            ws.write(row,11,stock_loss,normal_style_float)        #rusak
            ws.write(row,12,price_unit_loss,normal_style_float)
            ws.write(row,13,stock_loss_value,normal_style_float)
            ws.write(row,14,stock_akhir,normal_style_float)
            ws.write(row,15,stock_akhir_price,normal_style_float)
            ws.write(row,16,stock_akhir_value,normal_style_float)
            
            
            max_len[0]=len(str(no))+3 > max_len[0] and len(str(no))+3 or max_len[0]
            max_len[1]=len(str(product)) > max_len[1] and len(str(product)) or max_len[1]
            max_len[2]=len(str(stock_awal)) > max_len[2] and len(str(stock_awal)) or max_len[2]
            max_len[3]=len(str(stock_awal_price)) > max_len[3] and len(str(stock_awal_price)) or max_len[3]
            max_len[4]=len(str(stock_bought)) > max_len[4] and len(str(stock_bought)) or max_len[4]
            max_len[5]=len(str(stock_bought_price)) > max_len[5] and len(str(stock_bought_price)) or max_len[5]
            max_len[6]=len(str(stock_bought_value)) > max_len[6] and len(str(stock_bought_value)) or max_len[6]
            max_len[7]=len(str(stock_awal_value)) > max_len[7] and len(str(stock_awal_value)) or max_len[7]
            max_len[8]=len(str(stock_sold)) > max_len[8] and len(str(stock_sold)) or max_len[8]
            max_len[9]=len(str(price_unit_sold)) > max_len[9] and len(str(price_unit_sold)) or max_len[9]
            max_len[10]=len(str(stock_sold*price_unit_sold)) > max_len[10] and len(str(stock_sold*price_unit_sold)) or max_len[10]
            max_len[11]=len(str(stock_loss)) > max_len[11] and len(str(stock_loss)) or max_len[11]                    #rusak
            max_len[12]=len(str(price_unit_loss)) > max_len[12] and len(str(price_unit_loss)) or max_len[12]
            max_len[13]=len(str(stock_loss*price_unit_loss)) > max_len[13] and len(str(stock_loss*price_unit_loss)) or max_len[13]
            max_len[14]=len(str(stock_akhir)) > max_len[14] and len(str(stock_akhir)) or max_len[14]
            max_len[15]=len(str(stock_akhir_price)) > max_len[15] and len(str(stock_akhir_price)) or max_len[15]
            max_len[16]=len(str(stock_akhir_value)) > max_len[16] and len(str(stock_akhir_value)) or max_len[16]
           
            no+=1
            row+=1
        for x in range(0,17):
            ws.col(x).width=max_len[x]*256
                
            
        
        
laporan_produk_xls('report.laporan.produk.xls', 'stock.move', parser=laporan_produk_xls_parser)
            
            
            
            
            
            
            
        
        