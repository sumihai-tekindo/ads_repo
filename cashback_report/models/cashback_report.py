from openerp import models, fields, api, _

class cashback_report(models.TransientModel):
    _name="cashback.report"
    
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    
    
        
    @api.multi
    def print_report(self,):
        self.ensure_one()
        cbl_ids = self.env['account.cashback.line'].search([('start_date','>=',self.start_date),('end_date','<=',self.end_date)])
        list_cbl = [cbl.id for cbl in cbl_ids]
        datas={
            'model'    : 'account.cashback.line',
            "ids"    : list_cbl, #id record dari tabel account.cashback.lines
            'start_date':self.start_date,
            'end_date':self.end_date,
        }
        return{
            'type': 'ir.actions.report.xml',
            'report_name': 'cashback.report.xls',
            'datas': datas
        }