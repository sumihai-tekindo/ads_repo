from openerp import fields,models
from xml.dom.minidom import ReadOnlySequentialNamedNodeMap

class BusinessModel(models.Model):
    _name='business.model'
    
    
    business_model = fields.One2many("business.model.line","business_model_id")
    name = fields.Char(string='BMcode', required=True)
    
    type_id = fields.Many2one("business.type")
    date = fields.Date('Business Model Date', related="type_id.date", readonly=True)
    business_type = fields.Char('Business Model Type',related="type_id.business_type")

    
class BusinessModelLine(models.Model):
    _name='business.model.line'
    
    business_model_id = fields.Many2one("business.model")
    business_model_name = fields.Char(string='Business Model Name')
    business_model_date = fields.Date('Business Model Date')
    