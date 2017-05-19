# -*- coding: utf-8 -*-
# � 2016, Dedi Sinaga <dedi@sicepat.com>
# � 2016 Sumihai Teknologi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Cashback Reports',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'author': 'Andrean Wijaya',
    'website': '-',
    'description': """This modules provide Cashback Reports""",
    'depends': ['base','account_cash_back',"account"],
    'data': [
        'views/cashback_report_view.xml',
        'reports/cashback_report.xml',
    ],
    'installable': True,
}
