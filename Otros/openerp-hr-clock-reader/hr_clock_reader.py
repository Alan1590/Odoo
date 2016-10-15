# -*- encoding: utf-8 -*-
##############################################################################
#
#    Clock Reader for OpenERP
#    Copyright (C) 2004-2009 Moldeo Interactive CT
#    (<http://www.moldeointeractive.com.ar>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
import timeutils as tu
from lib.models import labels as clock_labels
from lib.models import default as clock_default
from lib.models import classes as clock_class
from lib.attendance_creator import AttendanceCreator, \
        MultipleAssignedCardError, NotAssignedCardError
import netsvc

logger = netsvc.Logger()

_uri_help = """Determines the URI string to connect to the clock. The URI is
determined by each model watch. In the case of F5, for example is:
udp://localhost:8000/"""

def setSome(A, B):
    return A != None and A or B

class hr_clock_reader_clock(osv.osv):
    _name = "hr_clock_reader.clock"
    _description = "Clock"
    _columns = {
        'name' : fields.char("Name", size=64, required=True),
        'uri': fields.char('URI', size=128, required=True, help=_uri_help),
        'model': fields.selection(clock_labels, 'Model', required=True),
        'location_id': fields.many2one('hr.department', 'Location',
                                       select=True, ondelete='set null'),
        'timeout': fields.integer('Timeout (sec)'),
        'create_unknown_employee': fields.boolean('Create Unknown Employeers'),
        'ignore_sign_inout': fields.boolean('Ignore sign in/outs'),
        'ignore_restrictions': fields.boolean('Ignore DB restrictions',
                                              help='You must remove attendance sign-in/out restrictions before use it.'),
        'complete_attendance': fields.boolean('Autocomplete sign in/out'),
        'clean_at_end': fields.boolean('Clean clock at the end'),
        'tolerance': fields.integer('Tolerance', help='In seconds, distance'
                                    ' bettweeen attendance with same action'
                                    ' understanded as the same attendance.'),
        'active': fields.boolean('Active'),
    }
    _sql_constraints = [
        ('uri', 'UNIQUE (uri)', 'The uri of the clock must be unique' )
    ]
    _order = 'uri asc'

    def load_attendances(self, cr, uid, ids=None,
             clean_at_end = None,
             complete_attendance = None,
             create_unknown_employee = None,
             ignore_sign_inout = None,
             ignore_restrictions = None,
             tolerance = None,
             context=None):
        AC = AttendanceCreator(cr, uid, context=context)
        card_err = {}
        empl_err = {}
        empl_id = {}
        err = []
        c = 0

        if ids==None:
            ids = self.search(cr, uid, [])

        from datetime import datetime
        import csv
        DEBUGFILE = open('/tmp/clock.%s.csv' % datetime.today(), 'w')
        DEBUGCSV  = csv.writer(DEBUGFILE)

        for clock in self.browse(cr, uid, ids):
            C = clock_class[clock.model](clock.uri, timeout=clock.timeout)

            if not C.connect():
                err.append("Can't connect with clock '%s'." % clock.name)
                continue

            for n, card_id, method, action, dt in C.attendances():
                DEBUGCSV.writerow((n, card_id, method, action, dt))

                assert isinstance(dt, tu.datetime)

                # Verifico que esta tarjeta no me haya traido problemas
                # previamente.
                if card_id in card_err:
                    DEBUGCSV.writerow((n, card_id, method, action, dt,"in card_err"))
                    logger.notifyChannel('wizard.hr_clock_reader', netsvc.LOG_DEBUG,
                                          '_read_clock: Card %i in the black list.'%card_id)
                    continue

                # Verificar si un empleado usa esa tarjeta
                if not card_id in empl_id:
                    DEBUGCSV.writerow((n, card_id, method, action, dt,"not in empl_id"))
                    try:
                        empl_id[card_id] = AC.employee_id(card_id)

                    except MultipleAssignedCardError, m:
                        DEBUGCSV.writerow((n, card_id, method, action, dt,"MultipleAssignedCardError",m))
                        card_err[card_id] = str(m)
                        continue

                    except NotAssignedCardError, m:
                        DEBUGCSV.writerow((n, card_id, method, action, dt,"NotAssignedCardError",m))
                        if setSome(create_unknown_employee,
                                   clock.create_unknown_employee):
                            empl_id[card_id] = AC.create_employee(card_id)
                        else:
                            card_err[card_id] = str(m)
                            continue

                # Verifico que este empleado no me haya traido problemas
                # previamente.
                if card_id in card_err:
                    DEBUGCSV.writerow((n, card_id, method, action, dt,"Employee in black list"))
                    logger.notifyChannel('wizard.hr_clock_reader', netsvc.LOG_DEBUG,
                                    '_read_clock: Employee %i in the black list.' %
                                                                   empl_id[card_id])
                    continue

                # Si esta todo bien con el empleado, cargo la asistencia.
                if AC.exists_attendance(empl_id[card_id], dt, action):
                    DEBUGCSV.writerow((n, card_id, method, action, dt,"Attendance yet loaded"))
                    logger.notifyChannel('hr_clock_reader.clock', netsvc.LOG_DEBUG,
                               'read: Attendance %i:%s:%s(%s) yet loaded.' %
                                    (empl_id[card_id], tu.dt2s(dt), action, method))
                    continue

                r = AC.create_attendance(empl_id[card_id], dt, action, method,
                                     tolerance=setSome(tolerance,
                                                       clock.tolerance),
                                     complete_attendance=setSome(complete_attendance, clock.complete_attendance),
                                     forgot_action=setSome(ignore_sign_inout, clock.ignore_sign_inout),
                                     ignore_restrictions=setSome(ignore_restrictions, clock.ignore_restrictions))

                if r == AttendanceCreator.OK:
                    DEBUGCSV.writerow((n, card_id, method, action, dt,"Creation Success"))
                    c = c + 1
                elif r == AttendanceCreator.IGNORED:
                    DEBUGCSV.writerow((n, card_id, method, action, dt,"Ignored"))
                else:
                    DEBUGCSV.writerow((n, card_id, method, action, dt,"Creation Error", r))
                    #logger.notifyChannel('hr_clock_reader.clock',
                    #     netsvc.LOG_INFO,
                    #     'read: Append employee %s to the black list.' %
                    #     str(empl_id[card_id]))
                    #empl_err[empl_id[card_id]] = str(m)

        DEBUGCSV.writerow((-1, -1, -1, -1, -1,"End process"))
        DEBUGFILE.close()

        # Recolección de errores
        cards_err = card_err.keys()
        empls_err = empl_err.keys()

        cards_err.sort()
        empls_err.sort()

        err += map(lambda i: card_err[i], cards_err)
        err += map(lambda i: empl_err[i], empls_err)

        return { 'count': c, 'errors': err }

hr_clock_reader_clock()

class hr_attendance(osv.osv):
    _inherit = "hr.attendance"
    _columns = {
        'method': fields.selection( [('manual', 'Manual'),
                                    ('automatic', 'Automatic'),
                                    ('keyboard', 'Keyboard'),
                                    ('fingerprint', 'Fingerprint'),
                                    ('rfid', 'RFid'),
                                    ('facerecognition', 'Face recognition'),],
                                   'Authentication method'),
        'auto_status': fields.selection( [('UNDEFINED','Undefined'),
                                        ('OK_START','Ok Start'),
                                        ('OK_START_I','Ok Start Interval'),
                                        ('OK_END_I','Ok End Interval'),
                                        ('OK_END','Ok End'),
                                        ('FORCED_START','Forced Ok Start'),
                                        ('FORCED_START_I','Forced Ok Start Interval'),
                                        ('FORCED_END_I','Forced Ok End Interval'),
                                        ('FORCED_END','Forced Ok End'),
                                        ('CREATED_START','Created Ok Start'),
                                        ('CREATED_START_I','Created Ok Start Interval'),
                                        ('CREATED_END_I','Created Ok End Interval'),
                                        ('CREATED_END','Created Ok End'),],
                                        'Automatic Attendance Status'),
    }

    _defaults = {
        'method': 'fingerprint',
        'auto_status': 'UNDEFINED',
    }

hr_attendance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
