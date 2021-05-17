# -*- coding: utf-8 -*-
from flask_restplus import Resource, Api, Namespace, fields
from .decorators import token_required, APIError
from flask import Blueprint, current_app, jsonify, json, g, abort
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, PAYMENT_TYPES, Request, REQUEST_TYPES, RequestFile, RequestBids
from .parsers import LoginParser
import re, os
from app import limiter
from .models_api import loginData, user_files, request_files, requestfileData, requestBIDData, requestBID_files
from datetime import datetime, timedelta
from utils import s3_get_pre_signed, s3_store_images, s3_delete_file
from werkzeug.datastructures import FileStorage

api_rest = Namespace('bids', description='bids module')

class SecureResource(Resource):
	method_decorators = [token_required]



bidsGET = api_rest.parser()
bidsGET.add_argument('limit', type=int, location='args')
bidsGET.add_argument('offset', type=int, location='args')



@api_rest.route('/')
class BidsAPI(SecureResource):
	@api_rest.doc(model=requestfileData, parser=bidsGET)
	def get(self):
		''' get my bids '''

		args = bidsGET.parse_args()

		query = RequestBids.query.filter(RequestBids.user_id==g.user.id)
		total = query.count()
		query = query.limit(args.get("limit", 25)).offset(args.get("offset", 0))
		data = [item.to_json() for item in query.all()]

		return jsonify(dict(success=True, total=total, data=data))





