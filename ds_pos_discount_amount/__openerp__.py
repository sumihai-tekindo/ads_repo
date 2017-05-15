{
    'name': 'PoS Amount Discount - POS',
    'version': '9.0.1.0.0',
    'category': 'web',
    'author': "Dedi Sinaga",
    'website': 'www.github.com/dedisinaga',
    'license': 'AGPL-3',
    'depends': [
        'web','point_of_sale','ds_pos_multi_company','account',
    ],
    'data': [
        'views/templates.xml',
        'views/pos_order_view.xml',
        'views/account_invoice_view.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'installable': True,
    'auto_install': False,
}