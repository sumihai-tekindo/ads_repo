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
	'depends': ['base','account'],
	'data': [
		'datas/res_company.xml',
		'datas/account_chart_template_aroma.xml',
		'datas/account_chart_template_arisma.xml',
		'datas/account_chart_template_aura.xml',
		'datas/account_chart_template.yml'
	],
	'installable': True,
	'auto_install': False,
}
