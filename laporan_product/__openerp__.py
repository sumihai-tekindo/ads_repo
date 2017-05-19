# -*- coding: utf-8 -*-
# � 2016, Dedi Sinaga <dedi@sicepat.com>
# � 2016 Sumihai Teknologi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Laporan Produk',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Reporting',
    'author': 'Andrean Wijaya',
    'website': '-',
    'description': """This modules provide Laporan Produk""",
    'depends': ['base',"account","product","report_xls"],
    'data': [
        'views/laporan_produk_view.xml',
        'reports/laporan_produk.xml',
    ],
    'installable': True,
}
