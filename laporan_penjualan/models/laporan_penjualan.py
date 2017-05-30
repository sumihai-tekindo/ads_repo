from openerp import models, fields, api, _

class laporan_penjualan(models.TransientModel):
    _name="laporan.penjualan"
    
    start_date = fields.Date(string="Start Date", required=True,default="2017-05-01")
    end_date = fields.Date(string="End Date", required=True,default="2017-05-31")
    report_type = fields.Selection([('laporan_penjualan','Online'),
                                    ('laporan_penjualan_off','Offline')],
                                   string="Report Type",required=True,default="laporan_penjualan")
    company_id = fields.Many2one('res.company',string='Company',required=True)
    account_ids = fields.Many2many(comodel_name='account.account',string='Accounts')
    
        
    @api.multi
    def print_report(self,):
        self.ensure_one()
        datas ={}
        company_id = self.company_id.id
        
        if self.report_type=='laporan_penjualan':
            analytic_id = self.env['account.analytic.account'].search([('online_type','=','online'),('company_id','=',self.company_id.id)])
            invoice_ids = self.env['account.invoice'].search([('analytic_account_id','in',[a.id for a in analytic_id]),('type','=','out_invoice'),('date','>=',self.start_date),('date','<=',self.end_date),('company_id','=',self.company_id.id),('state','in',('open','paid'))])
            # print "xxxxxxxxxxxxxxxxxxxxxxxxxx",invoice_ids
            datas={
                'model'    : 'account.invoice',
                "ids"    : [inv.id for inv in invoice_ids], 
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
            analytic_id = self.env['account.analytic.account'].search([('online_type','=','offline'),('company_id','=',self.company_id.id)])
            invoice_ids = self.env['account.invoice'].search([('analytic_account_id','in',[a.id for a in analytic_id]),('type','=','out_invoice'),('date','>=',self.start_date),('date','<=',self.end_date),('company_id','=',self.company_id.id),('state','in',('open','paid'))])
            datas={
                'model'    : 'account.invoice',
                "ids"    : [inv.id for inv in invoice_ids], 
                'start_date':self.start_date,
                'end_date':self.end_date,
                'report_type':self.report_type,
            }
            return{
                'type': 'ir.actions.report.xml',
                'report_name': 'laporan.penjualan.off.xls',
                'datas': datas
            } 
            
            
            
        