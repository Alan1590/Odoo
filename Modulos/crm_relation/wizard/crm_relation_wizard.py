from openerp.osv import fields, osv, models
from openerp.tools.translate import _

class crm_relation_lead(models.TransientModel):
    """ Crm claim plus location
    """
    _name = "crm.relation.wiz"
    _description = "Wizard for relations"
    _inherit = ['crm.case.stage']
    _columns = {
	'initial_state': fields.many2one('crm.case.stage', 'Initial State', readonly=True),
	'move_to_state': fields.many2one('crm.case.stage', 'Move to state', requiered=True),
	'update_value': fields.boolean('Update oportunity value'),
	}

    _default={
	'update_value': True,
	}

    def _update_stage_oportunity(self, cr, uid, context=None):
	return null
