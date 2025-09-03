# -*- coding: utf-8 -*-

{
    'name': 'Alzain - POS Extended',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'POS Extended',
    'description': 'POS Extended',
    'author': 'Adil Akbar',
    'depends': ['point_of_sale', 'hr'],
    'data': [
        "views/res_partner_views.xml",
        "views/pos_order_view.xml",
        "views/res_config_settings_views.xml",
        "views/pos_payment_method.xml"
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'gl_alzain_pos_extended/static/src/**/*',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
