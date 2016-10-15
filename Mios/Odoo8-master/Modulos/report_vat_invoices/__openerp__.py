# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Report tax',
    'version': '0.1',
    'category': 'Invoice',
    'description': """

Report Tax for invoice
=======================
Generate a quickly report for the tax of your invoices.

Account.invoice adds a menu to print the report or VAT , for a quick look , you can see a pop-up menu in the report of finance in the current window
    """,
    'author': 'Alan Gon',
    'website': 'https://www.facebook.com/alanxls.gon',
    'depends': ['account'],
    'data': [
        'views/report_vat_invoices_view.xml',
        'views/print_vat_invoices.xml',
        'wizard/report_vat_wizard_view.xml',
        # 'wizard/update_vat_wizard_view.xml'    
    
    ],
    'installable': True,
    'auto_install': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
