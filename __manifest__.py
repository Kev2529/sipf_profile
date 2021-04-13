# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "SIPF Profile",

    'summary': '',
    'description': """
Ce module permet de personnaliser Odoo pour le SIPF
""",
    'author': 'INVITU, Cyril VINH-TUNG',
    'website': 'http://www.invitu.com',

    'category': 'Custom',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'l10n_pf_public_purchase_ui_rename',
        'calendar',
        'project_template',
        'project_category',
        'project_task_dependency',
        'purchase_stock',
        'purchase_requisition',
    ],

    # always loaded
    'data': [
        'security/sipf_profile_security.xml',
        'security/ir.model.access.csv',
        'data/nomenclature.europe.csv',
        'data/analytic_account_data.xml',
        'data/project_type_data.xml',
        'views/product_views.xml',
        'views/project_views.xml',
        'views/purchase_views.xml',
        'views/purchase_requisition_views.xml',
        'views/account_move_views.xml',
        'views/nomenclature_views.xml',
        'views/analytic_account_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}
