# -*- encoding: utf-8 -*-
##############################################################################
#
#    Dedi Odolof Adelbert Sinaga
#    Copyright (C) 2016
#    
##############################################################################

{
	'name': 'Sales Commission ADS',
	'version': '1.0',
	'category': 'Localization',
	'summary': 'Sales Commission for ADS',
	'description': """
    This module compute sales commission for ADS
""",
	'website': 'http://dedisinaga.blogspot.com',
	'depends': ['base','account','sale','report_xls'],
	'data': [
		'views/commission_rule_view.xml',
		'views/commission_compute.xml',
		'views/commission_report_wizard_view.xml',
	],
	'installable': True,
	'auto_install': False,
}
