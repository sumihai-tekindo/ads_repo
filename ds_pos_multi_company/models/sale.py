from datetime import datetime, timedelta
from openerp import api, fields, models, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from openerp.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _default_warehouse_id(self):
    	res = super(SaleOrder,self)._default_warehouse_id()
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        res = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1)
        return res
    
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse',
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        default=_default_warehouse_id)
