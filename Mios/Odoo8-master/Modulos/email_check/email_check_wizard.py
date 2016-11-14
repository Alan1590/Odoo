from openerp import models, fields, api
from openerp.osv import fields, osv
import logging
import logging
logger = logging.getLogger(__name__)
class email_check_wizard(osv.osv):

    _name = "email.check.wizard"
    _description = "Check for email"
    _inherit = ["mail.mail","sale.order"]

    def launch_wizard(self):
    	logger.error("KJSFDJKSDFKJFDSKSFKJNFDSKJNFKJDFJFDJJJ")
    	return null	
