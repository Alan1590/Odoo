from openerp import models, fields, api
from openerp.osv import fields, osv
import logging
logger = logging.getLogger(__name__)

class report_vat_invoice(osv.osv):
    """ Print tax from invoice
    """
    _name = "report.vat.invoices"
    _description = "Print tax report"


    _columns = {
    	'name': fields.char(size=256,string="Name", required="True"),
        'date_start': fields.date(),
        'date_end': fields.date(),
        'company_id': fields.many2one('res.company',string="Company"),
        'invoices_id': fields.many2many('account.invoice',string="Invoices",limit=80),
        'tax_27': fields.float(computed="get_vat_amount"),
        'tax_21': fields.float(computed="get_vat_amount"),
        'tax_105': fields.float(computed="get_vat_amount"),
        'amount_vat': fields.float(computed="get_vat_amount"),
    }


    @api.multi
    @api.depends('invoices_id','tax_27','tax_21','tax_105')
    def get_vat_amount(self):
        self.tax_27 =0.0
        self.tax_21 =0.0
        self.tax_105 =0.0
        self.amount_vat=0.0
        for record in self.invoices_id:            
                for tax_list in record.tax_line:
                        #FACTURAS DE VENTA SEGUN IVA POSITIVO
                        if tax_list.name == '01003006:V' and record.journal_id.type=='sale':
                            self.tax_27 += tax_list.amount
                        elif tax_list.name == '01003005:V' and record.journal_id.type=='sale':
                            self.tax_21 += tax_list.amount                   
                        elif tax_list.name == '01003004:V' and record.journal_id.type=='sale':
                            self.tax_105 += tax_list.amount
                        #NOTAS DE CREDITOS IVA NEGATIVO
                        elif tax_list.name == '01003006:V' and record.journal_id.type=='sale_refund':
                            self.tax_27 -= tax_list.amount
                        elif tax_list.name == '01003005:V' and record.journal_id.type=='sale_refund':
                            self.tax_21 -= tax_list.amount                   
                        elif tax_list.name == '01003004:V' and record.journal_id.type=='sale_refund':
                            self.tax_105 -= tax_list.amount
                        #FACTURAS DE COMPRA IVA NEGATIVO
                        elif tax_list.name == '01003006:C' and record.journal_id.type=='purchase':
                            self.tax_27 -= tax_list.amount                        
                        elif tax_list.name == '01003005:C' and record.journal_id.type=='purchase':
                            self.tax_21 -= tax_list.amount                   
                        elif tax_list.name == '01003004:C' and record.journal_id.type=='purchase':
                            self.tax_105 -= tax_list.amount
                        #NOTAS DE CREDITOS FACTURAS COMPRA IVA POSITIVO   
                        elif tax_list.name == '01003006:C' and record.journal_id.type=='purchase_refund':
                            self.tax_27 += tax_list.amount
                        elif tax_list.name == '01003005:C' and record.journal_id.type=='purchase_refund':
                            self.tax_21 += tax_list.amount                   
                        elif tax_list.name == '01003004:C' and record.journal_id.type=='purchase_refund':
                            self.tax_105 += tax_list.amount
        self.amount_vat = self.tax_27 + self.tax_21 + self.tax_105                         




    # @api.one
    # @api.depends('amount_tax')
    # def _get_vat_partner(self):    	
    #     for invoices_customer in self:
    # 	    if self.journal_id.type == 'sale' or self.journal_id.type == 'purcharse_refund':
	   #  		self.amount_partner += invoices_customer.amount_tax


    # @api.one
    # @api.depends('amount_tax')
    # def _get_vat_supplier(self):
    # 	for invoices_supplier in self:
    #         if self.journal_id.type == 'purchase' or self.journal_id.type == 'sale_refund':
    #             self.amount_supplier += (invoices_supplier.amount_tax) * -1
                
