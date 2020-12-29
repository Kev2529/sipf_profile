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
        'calendar',
        'project_template',
        'project_category',
        'project_task_dependency',
        'purchase_requisition',
        'hr_holidays',
    ],

    # always loaded
    'data': [
        'views/project_views.xml',
        'views/purchase_views.xml',
        'views/purchase_requisition_views.xml',
        'views/account_move_views.xml',
        'views/nomenclature_views.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}
