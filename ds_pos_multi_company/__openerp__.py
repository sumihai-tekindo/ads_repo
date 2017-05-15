{
    'name': 'Multi Company - POS',
    'version': '9.0.1.0.0',
    'category': 'web',
    'author': "Dedi Sinaga",
    'website': 'www.github.com/dedisinaga',
    'license': 'AGPL-3',
    'depends': [
        'web','point_of_sale','pos_stock_avail','purchase','sale','stock',
    ],
    'data': [
        'views/template.xml',
        "views/pos_config_view.xml",
        "views/product_pricelist_view.xml",
        "views/product_view.xml",
        "views/pos_order_view.xml",
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'installable': True,
    'auto_install': False,
}