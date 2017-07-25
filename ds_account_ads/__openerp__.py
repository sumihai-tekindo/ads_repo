{
    'name': 'ADS Accounting',
    'version': '9.0.1.0.0',
    'category': 'Accounting',
    'author': "Dedi Sinaga",
    'website': 'www.github.com/dedisinaga',
    'license': 'AGPL-3',
    'depends': [
        'base','l10n_id','account','account_accountant','product'
    ],
    'data': [
        'datas/ir_sequence_aroma.xml',
        'datas/ir_sequence_arisma.xml',
        'datas/ir_sequence_aura.xml',
        'datas/account_journal_aroma.xml',
        'datas/account_journal_arisma.xml',
        'datas/account_journal_aura.xml',
        'datas/product_category.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': False,
}