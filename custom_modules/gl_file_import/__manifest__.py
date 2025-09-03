# -*- coding: utf-8 -*-
{
    'name': "GL File Import",
    'version': "1.0",
    'description': """GL File Import""",
    'summary': "GL File Import Customisation",
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}
