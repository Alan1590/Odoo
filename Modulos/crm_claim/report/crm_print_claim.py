import time
from openerp.report import report_sxw

class account_invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crm_claim, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
report_sxw.report_sxw(
    'report.crm.claim',
    'crm.claim',
    'addons/crm_claim/report/crm_print_claim_report.rml',
    #parser=crm_claim
)
