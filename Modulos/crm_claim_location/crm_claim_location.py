import openerp
from openerp.addons.crm import crm
from openerp.osv import fields, osv
from openerp import tools, api
from openerp.tools.translate import _
from openerp.tools import html2plaintext
import logging

class crm_claim_location(osv.osv):
    """ Crm claim plus location
    """
    _name = "crm.claim"
    _description = "Claim plus location"
    _inherit = ['crm.claim']
    _columns = {
        'partner_street': fields.char('Street',size=256),
        'partner_city': fields.char('City',size=256),
        'partner_state': fields.char('State',size=256),
        'partner_country': fields.char('Country',size=256),
	}

    def onchange_partner_id(self, cr, uid, ids, partner_id,context=None):
	value = super(crm_claim_location, self).onchange_partner_id(cr, uid, ids, partner_id,context=context)
	partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        value['value'].update({
                                'partner_street':partner.street,
                                'partner_city':partner.city,
                                'partner_state':partner.state_id.name,
                                'partner_country':partner.country_id.name,

        })
	return value
