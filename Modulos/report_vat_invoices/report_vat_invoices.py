from openerp import models, fields, api
from openerp.osv import fields, osv
import logging, calendar
logger = logging.getLogger(__name__)

class report_vat_invoices(osv.osv):
    """ Print tax from invoice
    """
    _name = "report.vat.invoices"
    _description = "Print tax report"


    _columns = {
    	'name': fields.char(size=256,string="Name", required="True"),
        'date_start': fields.date(required="True"),
        'date_end': fields.date(required="True"),
        'company_id': fields.many2one('res.company',string="Company"),
        'invoices_id': fields.many2many('account.invoice',string="Invoices"),
        'tax_27': fields.float(computed="get_vat_amount"),
        'tax_21': fields.float(computed="get_vat_amount"),
        'tax_105': fields.float(computed="get_vat_amount"),
        'total_vat_sale': fields.float(computed="get_vat_sale"),
        'total_vat_purchase': fields.float(computed="_get_vat_purchase"),  
        'total_vat_nc': fields.float(computed="_get_vat_nc"),        
        'amount_vat': fields.float(computed="_get_vat_amount"),
    }


    @api.multi
    def get_vat_amount(self):
        self.tax_27 = self._get_vat_27()
        self.tax_21 = self._get_vat_21()
        self.tax_105 = self._get_vat_105()
        self.total_vat_purchase = self._get_vat_purchase()
        self.total_vat_sale = self._get_vat_sale()
        self.total_vat_nc = self._get_vat_nc()
        self.amount_vat = self.tax_27 + self.tax_21 + self.tax_105                         

    def _get_vat_purchase(self):
        vat_purchase=0.0
        for record in self.invoices_id:
            if record.type=="in_invoice":
                vat_purchase -= record.amount_tax
        return vat_purchase

    def _get_vat_nc(self):
        vat_nc = 0.0
        for record in self.invoices_id:
            if record.type=="out_refund":
                vat_nc -= record.amount_tax
            elif record.type=='in_refund':
                vat_nc += record.amount_tax
        return vat_nc

    def _get_vat_sale(self):
        vat_sale = 0.0
        for record in self.invoices_id:
            if record.type=="out_invoice":
                vat_sale += record.amount_tax
        return vat_sale

    def _get_vat_27(self):
        tax_27 = 0
        for record in self.invoices_id:            
                for tax_list in record.tax_line:
                    if tax_list.name == '01003006:V':                        
                        tax_27 += tax_list.amount
                    elif tax_list.name == '01003006:C':
                        tax_27 -= tax_list.amount       
        return tax_27

    def _get_vat_21(self):
        tax_21=0.0
        for record in self.invoices_id:            
                for tax_list in record.tax_line:
                    if tax_list.name == '01003005:V':                        
                        tax_21 += tax_list.amount
                    elif tax_list.name == '01003005:C':
                        tax_21 -= tax_list.amount       
        return tax_21

    def _get_vat_105(self):
        tax_105 = 0.0
        for record in self.invoices_id:            
                for tax_list in record.tax_line:
                    if tax_list.name == '01003004:V':                        
                        tax_105 += tax_list.amount
                    elif tax_list.name == '01003004:C':
                        tax_105 -= tax_list.amount                   
        return tax_105

    @api.multi
    def fill_invoices_list(self):
        list_of_invoices = self.env['account.invoice'].search([('&'),('date_invoice','>=',self.date_start),
            ('date_invoice','<=',self.date_end),
            ('state','!=','draft'),('state','!=','cancel')])
        list_of_ids=[]
        for l_invoices in list_of_invoices:
            list_of_ids.append(l_invoices.id)
        self.write({'invoices_id':[(6, 0,list_of_ids)]})



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
                
