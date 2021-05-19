from functools import wraps
from models import User
from flask import request, jsonify, g, abort
import jwt
from flask_mail import Mail, Message
from jinja2 import Environment, BaseLoader


exclude_path = ['/apis/auth/validate-phone','/apis/auth/me']

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'apikey' in request.headers:
            token = request.headers['apikey']

        if not token:
            raise abort(401, 'a valid token is missing')

        try:
            from app import app
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")
            user = User.query.filter_by(id=data['id']).first()
            g.user = user
            if not user.is_phone_valid and request.path not in exclude_path:
                raise abort(401, 'please validate phone number')

            if user.is_disabled:
                raise abort(401, 'Account restricted, please contact our support team')

        except Exception as error:
            raise abort(401, str(error))

        return f(*args, **kwargs)
    return decorator


def onlyEmployer(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if g.user.user_type != "hire":
            raise abort(401, 'api limited only for employer')
        return f(*args, **kwargs)
    return decorator


class APIError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        data = dict(self.payload or ())
        data['message'] = self.message
        return dict(error=data)
