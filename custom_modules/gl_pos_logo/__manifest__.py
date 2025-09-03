# -*- coding: utf-8 -*-
#############################################################################

{
    'name': 'Point of Sale Logo',
    'version': '18.0.1.0.0',
    'summary': """Logo For Point of Sale Screen And Removed Powered By Odoo from POS Receipt""",
    'category': 'Point Of Sale',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/pos_assets_index.xml',
    ],
    'assets': {
            'point_of_sale._assets_pos': [
                'gl_pos_logo/static/src/xml/pos_screen_image_view.xml',
                'gl_pos_logo/static/src/xml/order_receipt.xml',
            ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
