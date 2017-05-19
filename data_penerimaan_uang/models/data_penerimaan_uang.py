from openerp import models, fields, api, _

class data_penerimaan_uang(models.TransientModel):
    _name="data.penerimaan.uang"
    
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    report_type = fields.Selection([('receipt_voucher','Receipt Voucher'),
                                    ('pelunasan_piutang_customer','Pelunasan Piutang Customer'),
                                    ('data_penerimaan_uang','Data Penerimaan Uang')],
                                   string="Report Type",required=True)
    account_ids = fields.Many2many(comodel_name='account.account',string='Accounts')
    journal_ids = fields.Many2many(comodel_name='account.journal', string ='Journals')
        
    @api.multi
    def print_report(self,):
        self.ensure_one()
        datas ={}
        if self.report_type=='data_penerimaan_uang':
            account_ids = [x.id for x in self.account_ids]
            mvl_ids = self.env['account.move.line'].search([('date','>=',self.start_date),('date','<=',self.end_date),('reconcile_id','=',False),
                                        ('account_id','in',account_ids),('credit','>',0.0),('statement_id','<>',False),('journal_id.type','in',['cash','bank'])])
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
                'report_name': 'data.penerimaan.uang.xls',
                'datas': datas
            }
            
        elif self.report_type=='receipt_voucher':
            account_ids = (x.id for x in self.account_ids)
            journal_ids = (x.id for x in self.journal_ids)
            
#             mvl_ids = self.env['account.move.line'].search([('date','>=',self.start_date),('date','<=',self.end_date),
#                                                             ('account_id','in',account_ids),('reconcile_id','!=',False),'|',('reconcile_partial_id','!=',False)
#                                                             ('credit','>',0.0), ('journal_id.type','in',['sale','sale_refund'])])
            query = """
                select coalesce(aml_rec.id,aml_prec.id)
                from account_move_line aml
                left join account_journal aj on aml.journal_id=aj.id
                left join account_move_line aml_rec on aml.reconcile_id=aml_rec.reconcile_id and aml.id!=aml_rec.id
                left join account_move_line aml_prec on aml.reconcile_partial_id = aml_prec.reconcile_partial_id and aml.id!=aml_prec.id
                left join account_journal aj_rec on aml_rec.journal_id=aj_rec.id
                left join account_journal aj_prec on aml_prec.journal_id=aj_prec.id
                where (aml.reconcile_id is not NULL or aml.reconcile_partial_id is not NULL) 
                and ((aml_rec.date>='%s' and aml_rec.date<='%s') or (aml_prec.date>='%s' and aml_rec.date<='%s'))
                and aj.type in ('sale','sale_refund') and (aj_rec.type in ('cash','bank') or aj_prec.type in ('cash','bank'))
                and aml.account_id in %s
                and (aj_rec.id in %s or aj_prec.id in %s)
                group by coalesce(aml_rec.id,aml_prec.id)
            """%(self.start_date,self.end_date,self.start_date,self.end_date,tuple(account_ids),tuple(journal_ids),tuple(journal_ids))
            
            self.env.cr.execute(query)
            res = self.env.cr.fetchall()
            
            mvl_ids2=self.env['account.move.line'].search([('date','>=',self.start_date),('date','<=',self.end_date),
                                                            ('account_id','in',account_ids),
                                                            ('credit','>',0.0), ('journal_id','in',journal_ids),
                                                            ('journal_id.type','in',['cash','bank'])])
            mvl_ids = mvl_ids2 + res
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
                'report_name': 'receipt.voucher.xls',
                'datas': datas
            }
            
            
        elif self.report_type=='pelunasan_piutang_customer':
            account_ids = [x.id for x in self.account_ids]
            journal_ids = [x.id for x in self.journal_ids]
            
            mvl_ids = self.env['account.move.line'].search([('date','>=',self.start_date),('date','<=',self.end_date),
                                                            ('reconcile_id','!=',False),'|',('reconcile_partial_id','!=',False),('account_id','in',account_ids),
                                                            ('credit','>',0.0), ('journal_id','in',journal_ids),
                                                            ('journal_id.type','in',['cash','bank'])])
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
                'report_name': 'pelunasan.piutang.customer.xls',
                'datas': datas
            }
            
            
            
        