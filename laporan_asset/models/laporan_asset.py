from openerp import models, fields, api, _

class perhitungan_ppn(models.TransientModel):
    _name="laporan.asset"
    
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    account_ids = fields.Many2many(comodel_name='account.account',string='Accounts')
    
    
    
    @api.multi
    def print_report(self,):
        self.ensure_one()
        account_ids = [x.id for x in self.env['account.account'].search([('user_type_id','=','Receivable')])]
        mvl_ids = self.env['account.asset.asset'].search([('date','>=',self.start_date),
                                                   ('date','<=',self.end_date), 
                                                   ])
        list_mvl= [mvl.id for mvl in mvl_ids]
        datas={
            'model'    : 'account.asset.asset',
            "ids"    : list_mvl, #id record dari tabel account.cashback.lines
            'start_date':self.start_date,
            'end_date':self.end_date,
        }
        return{
            'type': 'ir.actions.report.xml',
            'report_name': 'laporan.asset.xls',
            'datas': datas
        }