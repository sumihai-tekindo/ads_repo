
from openerp import api
from openerp import SUPERUSER_ID
from openerp.exceptions import AccessError
from openerp.osv import osv, fields
from openerp.sql_db import TestCursor
from openerp.tools import config
from openerp.tools.misc import find_in_path
from openerp.tools.translate import _
from openerp.addons.web.http import request
from openerp.tools.safe_eval import safe_eval as eval
from openerp.exceptions import UserError

import re
import time
import base64
import logging
import tempfile
import lxml.html
import os
import subprocess
from contextlib import closing
from distutils.version import LooseVersion
from functools import partial
from pyPdf import PdfFileWriter, PdfFileReader
from reportlab.graphics.barcode import createBarcodeDrawing


class Report(osv.Model):
	_inherit ="report"

	def render(self, cr, uid, ids, template, values=None, context=None):
		"""Allow to render a QWeb template python-side. This function returns the 'ir.ui.view'
		render but embellish it with some variables/methods used in reports.

		:param values: additionnal methods/variables used in the rendering
		:returns: html representation of the template
		"""

		dummy = super(Report,self).render(cr,uid,ids,template,values=values,context=context)
		if values is None:
			values = {}

		if context is None:
			context = {}

		context = dict(context, inherit_branding=True)  # Tell QWeb to brand the generated html
		view_obj = self.pool['ir.ui.view']

		user = self.pool['res.users'].browse(cr, uid, uid, context=context)
		if context.get('company_id',False):
			company_id = self.pool.get('res.company').browse(cr,uid,context.get('company_id'))
		else:
			company_id = user.company_id
		website = None
		if request and hasattr(request, 'website'):
			if request.website is not None:
				website = request.website
				context = dict(context, translatable=context.get('lang') != request.website.default_lang_code)
		values.update(
			time=time,
			context_timestamp=lambda t: fields.datetime.context_timestamp(cr, uid, t, context),
			editable=True,
			user=user,
			res_company=company_id,
			website=website,
		)

		result = Report
		return view_obj.render(cr, uid, template, values, context=context)