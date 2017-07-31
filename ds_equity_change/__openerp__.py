{
    "name": "Equity Change Statement",
    "version": "1.0",
    "depends": ["base","account","account_reports","report_xls"],
    "author": "Dedi - Adsoft",
    "category": "Account",
    "description": """
    This Module is use to provide equity change statement
    """,
    "init_xml": [],
    'update_xml': [
                    "views/equity_available_view.xml",
                    "views/equity_change_wizard_view.xml",
                   ],
    'demo_xml': [],
    'installable': True,
    'application':True,
}