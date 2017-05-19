# -*- coding: utf-8 -*-
# � 2016, Dedi Sinaga <dedi@sicepat.com>
# � 2016 Sumihai Teknologi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Data Penerimaan Uang',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Reporting',
    'author': 'Andrean Wijaya',
    'website': '-',
    'description': """This modules provide Daftar Penerimaan Uang""",
    'depends': ['base',"account"],
    'data': [
        'views/data_penerimaan_uang_view.xml',
        'reports/data_penerimaan_uang.xml',
    ],
    'installable': True,
}
