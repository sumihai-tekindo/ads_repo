from openerp import models, fields, api, _

class laporan_penjualan(models.TransientModel):
    _name="laporan.penjualan"
    
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    report_type = fields.Selection([('laporan_penjualan','Online'),
                                    ('laporan_penjualan_off','Offline')],
                                   string="Report Type",required=True)

    account_ids = fields.Many2many(comodel_name='account.account',string='Accounts')
    
        
    @api.multi
    def print_report(self,):
        self.ensure_one()
        datas ={}
        if self.report_type=='laporan_penjualan':
            account_ids = [x.id for x in self.env['account.account'].search([('user_type_id','=','Receivable')])]
            mvl_ids = self.env['account.move.line'].search([('date','>=',self.start_date),
                                                       ('date','<=',self.end_date),
                                                       ('account_id','in',account_ids), 
                                                       ])
            list_mvl= [mvl.id for mvl in mvl_ids]
            datas={
                'model'    : 'account.move.line',
                "ids"    : list_mvl, #id record dari tabel account.cashback.lines
                'start_date':self.start_date,
                'end_date':self.end_date,
                'report_type':self.report_type,
            }
            return{
                'type': 'ir.actions.report.xml',
                'report_name': 'laporan.penjualan.xls',
                'datas': datas
            }      

            
        elif self.report_type=='laporan_penjualan_off':
            account_ids = [x.id for x in self.env['account.account'].search([('user_type_id','=','Receivable')])]
            mvl_ids = self.env['account.move.line'].search([('date','>=',self.start_date),
                                                       ('date','<=',self.end_date),
                                                       ('account_id','in',account_ids), 
                                                       ])
            list_mvl= [mvl.id for mvl in mvl_ids]
            datas={
                'model'    : 'account.move.line',
                "ids"    : list_mvl, #id record dari tabel account.cashback.lines
                'start_date':self.start_date,
                'end_date':self.end_date,
                'report_type':self.report_type,
            }
            return{
                'type': 'ir.actions.report.xml',
                'report_name': 'laporan.penjualan.off.xls',
                'datas': datas
            } 
            
            
            
        