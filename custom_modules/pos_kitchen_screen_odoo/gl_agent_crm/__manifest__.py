# -*- coding: utf-8 -*-
{
    'name': "GL Agent Portal",
    'version': "1.0",
    'description': """GL Agent Portal""",
    'summary': "GL Agent Portal where agent selects the required modules for the client.",
    'depends': ['base','crm'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/crm_lead_view.xml',
        'views/price_configurator_view.xml',
        'wizard/reject_approval_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}
