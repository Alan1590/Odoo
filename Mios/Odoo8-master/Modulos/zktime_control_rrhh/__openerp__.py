
{
    'name': 'Control for zktime clock',
    'version': '0.1',
    'category': 'Fingerprint clock control',
    'description': """

Zktime fingerprint
==================
This module integrate zktime clock with odoo through HR

    """,
    'author': 'Alan Gon',
    'website': 'https://www.facebook.com/alanxls.gon',
    'depends': ['hr'],
    'data': [
        'views/zktime_data_conect.xml',        
        'views/zktime_control_view.xml'
    ],
    'installable': True,
    'auto_install': True,
}
