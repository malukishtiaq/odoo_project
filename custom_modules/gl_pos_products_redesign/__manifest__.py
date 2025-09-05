{
    'name': 'GL POS Products Redesign',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Custom redesign for POS Products page with modern styling',
    'description': """
        Custom module to redesign the POS Products page with:
        - Modern product card design
        - Enhanced visual styling
        - Improved user experience
        - Custom animations and effects
    """,
    'author': 'GreenLines',
    'depends': ['point_of_sale', 'web'],
    'data': [
        'views/pos_product_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'gl_pos_products_redesign/static/src/xml/product_templates.xml',
            'gl_pos_products_redesign/static/src/scss/product_redesign.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
