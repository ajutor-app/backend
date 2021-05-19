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

api_rest = Namespace('requests', description='requests module')

class SecureResource(Resource):
	method_decorators = [token_required]



helpRequestParser = api_rest.parser()
helpRequestParser.add_argument('title', type=str, required=True, help='title')
helpRequestParser.add_argument('description', type=str, required=True, help='description')
helpRequestParser.add_argument('payment_type', type=str, choices=list(PAYMENT_TYPES), required=True, help='payment type')
helpRequestParser.add_argument('request_type', type=str, choices=list(REQUEST_TYPES), required=True, help='request type')
helpRequestParser.add_argument('skills', type=int, action="append", help='skills_ids')


@api_rest.route('/create')
class HelpRequestAPI(SecureResource):
	decorators = [limiter.limit("10/minute")]

	@api_rest.doc(parser=helpRequestParser, model=request_files)
	def post(self):
		""" create temp request """

		args = helpRequestParser.parse_args()

		new_request = Request(
			user_id=g.user.id,
			title=args.get("title"),
			description=args.get("description"),
			payment_type=args.get("payment_type"),
			request_type=args.get("request_type"),
		)

		new_request.save()


		return jsonify(new_request.to_json())


UpdateRequestParser = api_rest.parser()
UpdateRequestParser.add_argument('title', type=str, required=True, help='title')
UpdateRequestParser.add_argument('description', type=str, required=True, help='description')
UpdateRequestParser.add_argument('payment_type', type=str, choices=list(PAYMENT_TYPES), required=True, help='payment type')
UpdateRequestParser.add_argument('request_type', type=str, choices=list(REQUEST_TYPES), required=True, help='request type')
UpdateRequestParser.add_argument('skills', type=int, action="append", help='skills_ids')


@api_rest.route('/<int:request_id>')
class RequestsAPI(SecureResource):
	@api_rest.doc(model=request_files)
	def get(self, request_id):
		''' get request_id details '''

		request = Request.query.filter_by(id=request_id).first()
		if request:
			return jsonify(request.to_json())


		return abort(404, "request_id not found")

	@api_rest.doc(parser=UpdateRequestParser, model=request_files)
	def put(self, request_id):
		''' update request_id details '''

		args = UpdateRequestParser.parse_args()

		request = Request.query.filter_by(id=request_id, user_id=g.user.id).first()
		if request:
			request.update_from_dict(request)

			return jsonify(request.to_json())

		return abort(404, "request_id not found")


	def delete(self, request_id):
		''' delete request_id '''

		request = Request.query.filter_by(id=request_id, user_id=g.user.id).first()
		if request:
			request.delete()

			return jsonify(dict(success=True))

		return abort(404, "request_id not found")


FileRequestParser = api_rest.parser()
FileRequestParser.add_argument('file', type=FileStorage, required=True, help='file')


@api_rest.route('/<int:request_id>/files')
class RequestsFilesAPI(SecureResource):
	@api_rest.doc(model=requestfileData)
	def get(self, request_id):
		''' get files of request_id '''

		items = RequestFile.query.filter_by(request_id=request_id).all()

		data = [item.to_json() for item in items]

		return jsonify(dict(success=True, total=len(data), data=data))

	@api_rest.doc(parser=FileRequestParser)
	def post(self, request_id):
		''' add file to request_id '''

		args = FileRequestParser.parse_args()

		if args.file:
			now = datetime.now()
			filename = "{}_{}".format(now.strftime("%d_%m_%Y_%H_%M_%S"), args.file.filename)
			filepath ='request/{}/{}'.format(request_id, filename)
			s3_store_images(args.file, filepath)
			
			file = RequestFile(
				request_id=request_id,
				user_id=g.user.id,
				filename=filepath,
			)
			file.save()

			return jsonify(file.to_json())


		return abort(400, "bad request")






