from openerp import models,fields

class InheritType(models.Model):
    _inherit="business.type"
    
    cost = fields.Char(string="Business Cost", required=True)