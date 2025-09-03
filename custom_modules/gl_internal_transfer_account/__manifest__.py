# -*- coding: utf-8 -*-
{
    'name': "GL Account Internal Transfer",
    'version': "1.0",
    'description': """GL Account Internal Transfer""",
    'summary': "GL Account Internal Transfer Customisation",
    'depends': ['account'],
    'data': [
        'views/account_payment_view.xml',
        'views/account_account_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}
