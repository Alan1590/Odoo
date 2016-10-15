from openerp import models, fields, api
from openerp.osv import fields, osv
import logging
logger = logging.getLogger(__name__)

class report_vat_invoice(osv.osv):
    """ Print tax from invoice
    """
    _name = "account.invoice"
    _description = "Print tax report"
    _inherit = ['account.invoice']


    _columns = {
    	'amount_partner': fields.float(compute="_get_vat_partner", string="amount partner", store=True),
    	'amount_supplier': fields.float(compute="_get_vat_supplier", string="amount supplier",store=True)
    }


    @api.one
    @api.depends('amount_tax')
    def _get_vat_partner(self):    	
        for invoices_customer in self:
    	    if self.journal_id.type == 'sale' or self.journal_id.type == 'purcharse_refund':
	    		self.amount_partner += invoices_customer.amount_tax


    @api.one
    @api.depends('amount_tax')
    def _get_vat_supplier(self):
    	for invoices_supplier in self:
            if self.journal_id.type == 'purchase' or self.journal_id.type == 'sale_refund':
                self.amount_supplier += (invoices_supplier.amount_tax) * -1
                
