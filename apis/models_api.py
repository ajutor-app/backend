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
