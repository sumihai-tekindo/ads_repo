# -*- encoding: utf-8 -*-
##############################################################################
#
#    Dedi Odolof Adelbert Sinaga
#    Copyright (C) 2016
#    
##############################################################################

{
	'name': 'COA - ADS',
	'version': '1.0',
	'category': 'Localization',
	'summary': 'Chart of Account for ADS',
	'description': """
    This module add chart of account for PT.ADS with MultiCompany
""",
	'website': 'http://dedisinaga.blogspot.com',
	'depends': ['base','account','stock'],
	'data': [
		'datas/res_company.xml',
		'datas/warehouses.xml',
		'datas/stock_location.xml',
		'datas/account_chart_template_aroma_2.xml',
		'datas/account_chart_template_arisma_2.xml',
		'datas/account_chart_template_aura_2.xml',
		'datas/account_chart_template.yml'
	],
	'installable': True,
	'auto_install': False,
}
