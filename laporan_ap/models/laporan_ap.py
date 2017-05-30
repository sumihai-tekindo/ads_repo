from openerp import models, fields, api, _

class laporan_ap(models.TransientModel):
    _name="laporan.ap"
    
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    type = fields.Selection([('piutang','Piutang(AR)'),
                                    ('hutang','Hutang(AP)')],
                            string="Report Type",required=True)
    info = fields.Selection([('partner','Per Partner'),
                                    ('summary','Summary')],
                                   string="Report Info",required=True)
    company_id = fields.Many2one('res.company','Company',required=True)
    
    @api.multi
    def print_report(self,):
        self.ensure_one()
        datas ={}
        if self.type=='hutang' and self.info=='partner':
            inv_ids = self.env['account.invoice'].search([('date','>=',self.start_date),
                                                          ('date','<=',self.end_date),
                                                          ('type','=','in_invoice'),
                                                          ('state','in',['open','paid']),
                                                          ('company_id','=',self.company_id.id)
                                                          ])
            list_inv= [inv.id for inv in inv_ids]
            datas={
                'model'    : 'account.invoice',
                "ids"    : list_inv, #id record dari tabel account.cashback.lines
                'start_date':self.start_date,
                'end_date':self.end_date,
                'type':self.type,
                'info':self.info,
            }
            return{
                'type': 'ir.actions.report.xml',
                'report_name': 'laporan.ap.xls',
                'datas': datas
            }
            
        elif self.type=='hutang' and self.info=='summary':
            inv_ids = self.env['account.invoice'].search([('date','>=',self.start_date),
                                                          ('date','<=',self.end_date),
                                                          ('type','=','in_invoice'),
                                                          ('state','in',['open','paid']),
                                                          ('company_id','=',self.company_id.id),
                                                          ])
            list_inv= [inv.id for inv in inv_ids]
            datas={
                'model'    : 'account.invoice',
                "ids"    : list_inv, #id record dari tabel account.cashback.lines
                'start_date':self.start_date,
                'end_date':self.end_date,
                'type':self.type,
                'info':self.info,
            }
            return{
                'type': 'ir.actions.report.xml',
                'report_name': 'summary.ap.xls',
                'datas': datas
            }
        
        
        elif self.type=='piutang' and self.info=='partner':
            inv_ids = self.env['account.invoice'].search([('date','>=',self.start_date),
                                                          ('date','<=',self.end_date),
                                                          ('type','=','out_invoice'),
                                                          ('state','in',['open','paid']),
                                                          ('company_id','=',self.company_id.id),
                                                          ])
            list_inv= [inv.id for inv in inv_ids]
            datas={
                'model'    : 'account.invoice',
                "ids"    : list_inv, #id record dari tabel account.cashback.lines
                'start_date':self.start_date,
                'end_date':self.end_date,
                'type':self.type,
                'info':self.info,
            }
            return{
                'type': 'ir.actions.report.xml',
                'report_name': 'laporan.ar.xls',
                'datas': datas
            }
            
        elif self.type=='piutang' and self.info=='summary':
            inv_ids = self.env['account.invoice'].search([('date','>=',self.start_date),
                                                          ('date','<=',self.end_date),
                                                          ('type','=','out_invoice'),
                                                          ('state','in',['open','paid']),
                                                          ('company_id','=',self.company_id.id),
                                                          ])
            list_inv= [inv.id for inv in inv_ids]
            datas={
                'model'    : 'account.invoice',
                "ids"    : list_inv, #id record dari tabel account.cashback.lines
                'start_date':self.start_date,
                'end_date':self.end_date,
                'type':self.type,
                'info':self.info,
            }
            return{
                'type': 'ir.actions.report.xml',
                'report_name': 'summary.ar.xls',
                'datas': datas
            }