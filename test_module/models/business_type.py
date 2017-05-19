from openerp import models, fields, api, _

class BusinessType(models.Model):
    _name = 'business.type'
    
    name = fields.Char(string='code', required=True)
    business_type = fields.Char(string='Business Type', required=True)
    date = fields.Date('Business Date')
    datetime = fields.Datetime('Business DateTime')
    