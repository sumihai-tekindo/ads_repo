{
    'name': 'Account Report Multi Company',
    'version': '9.0.1.0.0',
    'category': 'Accounting',
    'author': "Dedi Sinaga",
    'website': 'www.github.com/dedisinaga',
    'license': 'AGPL-3',
    'depends': [
        'report','account',
    ],
    'data': [
        'views/account_financial_report_view.xml',
        'views/account_report_aged_partner_balance_view.xml',
        'views/account_report_trial_balance_view.xml',
        'views/account_report_general_ledger_view.xml',
        
    ],
    'qweb': [
        
    ],
    'installable': True,
    'auto_install': False,
}