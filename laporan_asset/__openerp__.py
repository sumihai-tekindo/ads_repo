# -*- coding: utf-8 -*-
# � 2016, Dedi Sinaga <dedi@sicepat.com>
# � 2016 Sumihai Teknologi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Laporan Asset',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Reporting',
    'author': 'Andrean Wijaya',
    'website': '-',
    'description': """This modules provide Laporan Asset""",
    'depends': ['base',"account",'report_xls','account_asset'],
    'data': [
        'views/laporan_asset_view.xml',
        'reports/laporan_asset.xml',
    ],
    'installable': True,
}
