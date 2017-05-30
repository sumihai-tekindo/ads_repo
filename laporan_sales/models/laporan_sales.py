from openerp import models, fields, api, _

class perhitungan_ppn(models.TransientModel):
    _name="laporan.sales"
    
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    sale_type= fields.Selection([('offline','Offline'),('online','Online'),('summary','Summary')],required=True)
    company_id = fields.Many2one('res.company',"Company",required=True)
    
    
    
    @api.multi
    def print_report(self,):
        self.ensure_one()
        comm_detail = self.env['commission.compute.line.detail']
        domain_date = [('start_date','>=',self.start_date),('end_date','<=',self.end_date),('company_id','=',self.company_id.id)]
        if self.sale_type=='online':
            domain = domain_date+[('rule_type','in',['whs_on','ret_on'])]
        elif self.sale_type =='offline':
            domain = domain_date+[('rule_type','in',['whs_off','ret_off'])]
        else:
            domain = domain_date

        list_data = [x.id for x in comm_detail.search(domain)]

        datas={
            'model'    : 'commission.compute.line.detail',
            "ids"    : list_data, #id record dari tabel account.cashback.lines
            'start_date':self.start_date,
            'end_date':self.end_date,
        }
        return{
            'type': 'ir.actions.report.xml',
            'report_name': 'laporan.comm.'+self.sale_type+'.xls',
            'datas': datas
        }