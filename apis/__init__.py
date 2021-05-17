# -*- coding: utf-8 -*-
from flask_restplus import Resource, Api
from flask import Blueprint, url_for

description = '''
This is a simple app for call experts for solve home problems ( uber for experts ).

NOTE: Open API for open minds developers.

Postman export : https://api.ajutor.app/apis/postman.json
<style>.models {display: none !important}</style>
'''

authorizations = {
	'apikey': {
		'type': 'apiKey',
		'in': 'header',
		'name': 'apikey'
	}
}

api_bp = Blueprint('api_bp', __name__, url_prefix='/apis')

class MyApi(Api):
	@property
	def specs_url(self):
		"""Monkey patch for HTTPS"""
		scheme = 'http' if '5000' in self.base_url else 'https'
		return url_for(self.endpoint('specs'), _external=True, _scheme=scheme)

api_rest = MyApi(api_bp,
	authorizations=authorizations,
	title='Ajutor.app API',
	version='1.0',
	description=description,
	#doc=False
)


def apikey(func):
	return api_rest.doc(security='apikey')(func)


@api_bp.route("/postman.json", methods=["get"])
def ExportPostman():
	''' export postman colection ready for test '''
	return api_rest.as_postman(urlvars=False, swagger=True)


@api_bp.after_request
def add_header(response):
	response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
	return response


from .auth import api_rest as auth_api
api_rest.add_namespace(auth_api)

from .requests import api_rest as requests_api
api_rest.add_namespace(requests_api)

from .bids import api_rest as bids_api
api_rest.add_namespace(bids_api)


