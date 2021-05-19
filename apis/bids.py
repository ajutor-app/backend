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



BIDRequestParser = api_rest.parser()
BIDRequestParser.add_argument('price', type=float, required=True, help='price')
BIDRequestParser.add_argument('description', type=str, required=True, help='description')
BIDRequestParser.add_argument('delivery_time', type=datetime, required=True, help='delivery/jobdone time')


@api_rest.route('/<int:request_id>/bid')
class RequestsBidAPI(SecureResource):
	@api_rest.doc(model=requestBIDData)
	def get(self, request_id):
		''' get bids for request_id '''

		request = Request.query.filter_by(id=request_id).first()
		if not request:
			return abort(404, "request_id not found")

		if request.user_id != g.user.id:
			return abort(401, "Not have permisions !!!")

		items = RequestBids.query.filter_by(request_id=request_id).all()

		data = [item.to_json() for item in items]

		return jsonify(dict(success=True, total=len(data), data=data))

	@api_rest.doc(parser=BIDRequestParser, model=requestBID_files)
	def post(self, request_id):
		''' post bid for request_id '''

		args = BIDRequestParser.parse_args()

		request = Request.query.filter_by(id=request_id).first()
		if not request:
			return abort(404, "request_id not found")

		if request.user_id == g.user.id:
			return abort(401, "Not have permisions to publish bid to your requests.")

		new = RequestBids(
				request_id=request_id,
				user_id=g.user.id,
				delivery_time=args.get('delivery_time'),
				price=args.get('price'),
				description=args.get('description'),
			)
		new.save()

		return jsonify(new.to_json())


@api_rest.route('/bid/<int:request_bid_id>')
class RequestBidAPI(SecureResource):
	@api_rest.doc(model=requestBID_files)
	def get(self, request_bid_id):
		''' get details request_bid_id '''
		
		item = RequestBids.query.filter_by(id=request_bid_id).first()
		if not item:
			return abort(404, "request_bid_id not found")

		return jsonify(item.to_json())

	def delete(self, request_bid_id):
		''' delete request_bid_id '''

		item = RequestBids.query.filter_by(id=request_bid_id).first()
		if item and item.user_id == g.user.id:
			item.delete()

			return jsonify(dict(success=True))

		return abort(404, "request_bid_id not found")

	@api_rest.doc(parser=BIDRequestParser, model=requestBID_files)
	def put(self, request_bid_id):
		''' update request_bid_id '''

		args = BIDRequestParser.parse_args()

		item = RequestBids.query.filter_by(id=request_bid_id).first()
		if not item:
			return abort(404, "request_bid_id not found")

		if item.user_id != g.user.id:
			return abort(403, "not have permisions")

		item.update_from_dict(args)


		return jsonify(item.to_json())



