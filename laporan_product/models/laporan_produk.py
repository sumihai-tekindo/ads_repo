from openerp import models, fields, api, _

class laporan_produk(models.TransientModel):
    _name="laporan.produk"
    
    start_date = fields.Datetime(string="Start Date", required=True)
    end_date = fields.Datetime(string="End Date", required=True)
    report_type = fields.Selection([('laporan_produk','Laporan Produk'),
                                    ('ranking_penjualan','Ranking Penjualan'),
                                    ('range_margin','Range Margin')],
                                   string="Report Type",required=True)
    invoice_state = fields.Selection([('paid', 'Paid'),('open_paid', 'Open and Paid'),('draft_open_paid', 'Draft, Open and Paid'),], string='Invoice State', required=False)
    
    @api.multi
    def print_report(self,):
        self.ensure_one()
        datas={}
        if self.report_type=='laporan_produk':
            product_ids = [x.id for x in self.env['product.product'].search([('sale_ok','=',True),('type','=','product')])]
            location_ids = [x.id for x in self.env['stock.location'].search([('usage','=','internal')])]
            location_dest_ids = [x.id for x in self.env['stock.location'].search([('usage','=','customer')])]
            
            mv_ids = self.env['stock.move'].search([('date','>=',self.start_date),('date','<=',self.end_date),('state','=','done'),
                                          ('product_id','in',product_ids),('location_id','in',location_ids),('location_dest_id','in',location_dest_ids)
                                          ])
            list_mv = [mv.id for mv in mv_ids]
            
            datas={
                'model'    : 'stock.move',
                "ids"    : list_mv,
                'start_date':self.start_date,
                'end_date':self.end_date,
                'product_ids':product_ids,
            }
            return{
                'type': 'ir.actions.report.xml',
                'report_name': 'laporan.produk.xls',
                'datas': datas
            }
            
        elif self.report_type=='ranking_penjualan':
            
            product_ids = [x.id for x in self.env['product.product'].search([('sale_ok','=',True),('type','=','product')])]
            location_ids = [x.id for x in self.env['stock.location'].search([('usage','=','internal')])]
            location_dest_ids = [x.id for x in self.env['stock.location'].search([('usage','=','customer')])]
            mv_ids = self.env['stock.move'].search([('date','>=',self.start_date),('date','<=',self.end_date),('state','=','done'),
                                          ('product_id','in',product_ids),('location_id','in',location_ids),('location_dest_id','in',location_dest_ids)
                                          ])
            
            list_mv = [mv.id for mv in mv_ids]
            print "==== ranking penjualan=======",list_mv
            
            datas={
                'model'    : 'stock.move',
                "ids"    : list_mv,
                'start_date':self.start_date,
                'end_date':self.end_date,
                'product_ids':product_ids,
            }
            return{
                'type': 'ir.actions.report.xml',
                'report_name': 'ranking.penjualan.xls',
                'datas': datas
            }
            
        elif self.report_type=='range_margin':
            product_ids = [x.id for x in self.env['product.product'].search([('sale_ok','=',True)])]
            
            datas={
                'model'    : 'stock.move',
                "ids"    : product_ids,
                'start_date':self.start_date,
                'end_date':self.end_date,
                'product_ids':product_ids,
                'invoice_state':self.invoice_state
            }
            return{
                'type': 'ir.actions.report.xml',
                'report_name': 'range.margin.xls',
                'datas': datas
            }