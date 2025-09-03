# -*- coding: utf-8 -*-

{
    'name': 'Alzain - POS Receipt custom logo',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'POS Receipt Extended',
    'description': 'POS Receipt Extended',
    'author': 'Adil Akbar',
    'depends': ['point_of_sale'],
    'data': [
        "views/res_config_settings_views.xml",
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'gl_alzain_pos_receipt_logo/static/src/**/*',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
