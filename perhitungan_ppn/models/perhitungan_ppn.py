from openerp import models, fields, api, _

class perhitungan_ppn(models.TransientModel):
    _name="perhitungan.ppn"
    
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    tax1_id = fields.Many2one("account.tax.code",string="DPP Tax")
    tax2_id = fields.Many2one("account.tax.code",string="Tax")
    
    
    
    @api.multi
    def print_report(self,):
        self.ensure_one()
        tax_ids = [self.tax1_id.id,self.tax2_id.id]
        mvl_ids = self.env['account.move.line'].search([('date','>=',self.start_date),('date','<=',self.end_date), ('tax_code_id','in',tax_ids)])
        list_mvl= [mvl.id for mvl in mvl_ids]
        datas={
            'model'    : 'account.move.line',
            "ids"    : list_mvl, #id record dari tabel account.cashback.lines
            'start_date':self.start_date,
            'end_date':self.end_date,
        }
        return{
            'type': 'ir.actions.report.xml',
            'report_name': 'perhitungan.ppn.xls',
            'datas': datas
        }