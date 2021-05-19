from . import api_rest
from flask_restplus import inputs
import time
from datetime import datetime, timedelta
from werkzeug.datastructures import FileStorage
from models import UserType


# /login
LoginParser = api_rest.parser()
LoginParser.add_argument('email', type=inputs.email(), required=True, help='email')
LoginParser.add_argument('password', type=str, required=True, help='password')
LoginParser.add_argument('otp', type=str, help='otp')


RegisterParser = api_rest.parser()
RegisterParser.add_argument('email', type=inputs.email(), required=True, help='email')
RegisterParser.add_argument('phone', type=str, required=True, help='phone number')
RegisterParser.add_argument('password', type=str, required=True, help='password')
RegisterParser.add_argument('first_name', type=str, required=True, help='first_name')
RegisterParser.add_argument('last_name', type=str, required=True, help='last_name')
RegisterParser.add_argument('user_type', type=str, choices=list(UserType), required=True, help='last_name')
RegisterParser.add_argument('invite_code', type=str, help='invite_code')


SMSParser = api_rest.parser()
SMSParser.add_argument('sms_code', type=int, required=True, help='sms code')

UserParser = api_rest.parser()
UserParser.add_argument('email', type=inputs.email(), required=True, help='email', location='form')
UserParser.add_argument('first_name', type=str, required=True, help='first_name', location='form')
UserParser.add_argument('last_name', type=str, required=True, help='last_name', location='form')
UserParser.add_argument('phone', type=str, required=True, help='phone number', location='form')
UserParser.add_argument('city', type=str, required=True, help='city', location='form')
UserParser.add_argument('address', type=str, required=True, help='address', location='form')
UserParser.add_argument('country', type=str, required=True, help='country', location='form')
UserParser.add_argument('tz', type=str, required=True, help='timezone', location='form')
UserParser.add_argument('language', type=str, required=True, help='language', location='form')
UserParser.add_argument('avatar', type=FileStorage, required=True, help='user image', location='files')


# /login twofa
twofaParser = api_rest.parser()
twofaParser.add_argument('otp', type=int, required=True, help='otp')

ChangePasswordParser = api_rest.parser()
ChangePasswordParser.add_argument('password', type=str, required=True, help='password')
ChangePasswordParser.add_argument('new_password', type=str, required=True, help='new_password')

ForgotPasswordParser = api_rest.parser()
ForgotPasswordParser.add_argument('email', type=inputs.email(), required=True, help='email')

ResetPasswordParser = api_rest.parser()
ResetPasswordParser.add_argument('email', type=inputs.email(), required=True, help='email')
ResetPasswordParser.add_argument('email-code', type=str, required=True, help='email code')
ResetPasswordParser.add_argument('newpassword', type=str, required=True, help='new password')







