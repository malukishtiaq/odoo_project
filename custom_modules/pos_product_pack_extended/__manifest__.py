# -*- coding: utf-8 -*-

{
    'name': 'Hide Components In Pos Receipt',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Hide Components In Pos Receipt',
    'description': 'Hide Components In Pos Receipt',
    'author': 'Adil Akbar',
    'depends': ['point_of_sale', 'hr'],
    'data': [
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_product_pack_extended/static/src/js/pos_order.js',
            'pos_product_pack_extended/static/src/js/TicketScreen.js',
            'pos_product_pack_extended/static/src/xml/receipt_templates.xml',
            'pos_product_pack_extended/static/src/xml/order_widget.xml',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
