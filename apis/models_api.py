from flask_restplus import Namespace, Resource, fields
from . import api_rest

user_files = api_rest.model('User', {
    'id': fields.Integer,
    'email': fields.String,
    'full_name': fields.String,
    'user_type': fields.String,
    'is_admin': fields.Boolean,
    'tz':fields.String,
    'avatar':fields.String,
    'stats':fields.Raw(),
    'updated_at': fields.String,
    'created_at': fields.String,
})

loginData = api_rest.model('LoginData', {
    'success': fields.Boolean,
    'token': fields.String,
    'data': fields.List(fields.Nested(user_files)),
})


request_files = api_rest.model('Request', {
    'id': fields.Integer,
    'user_id': fields.String,
    'title': fields.String,
    'description': fields.String,
    'skills': fields.Raw(),
    'files':fields.Raw(),
    'updated_at': fields.String,
    'created_at': fields.String,
})

requestsData = api_rest.model('RequestData', {
    'success': fields.Boolean,
    'token': fields.String,
    'data': fields.List(fields.Nested(request_files)),
})

requestfile_files = api_rest.model('Request', {
    'id': fields.Integer,
    'filename': fields.String,
    'attachment_id': fields.String,
    'url': fields.String,
    'created_at': fields.String,
})


requestfileData = api_rest.model('RequestFileData', {
    'success': fields.Boolean,
    'token': fields.String,
    'data': fields.List(fields.Nested(requestfile_files)),
})



