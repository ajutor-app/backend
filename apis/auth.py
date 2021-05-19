# -*- coding: utf-8 -*-
from flask_restplus import Resource, Api, Namespace, fields
from .decorators import token_required, APIError
from flask import Blueprint, current_app, jsonify, json, g, abort
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from .parsers import LoginParser, ChangePasswordParser, ForgotPasswordParser,\
         ResetPasswordParser, twofaParser, RegisterParser, UserParser, SMSParser
from models.db import db
import re, os, random
from app import limiter
from .models_api import loginData, user_files
from datetime import datetime, timedelta
from utils import s3_get_pre_signed, s3_store_images, s3_delete_file

api_rest = Namespace('auth', description='auth module')

class SecureResource(Resource):
    method_decorators = [token_required]


@api_rest.route('/login')
class Login(Resource):
    decorators = [limiter.limit("10/minute")]

    @api_rest.doc(parser=LoginParser, model=loginData)
    def post(self):
        """ login user api """
        args = LoginParser.parse_args()

        user = User.query.filter(User.email==args.get('email')).first()
        if user and user.verify_password(args.get('password')):
            if user.is_disabled:
                return abort(401, "Account restricted, please contact us !!!")

            if user.twoFALoggedin:
                if not args.get('otp'):
                    return abort(401, "otp code is requested")
                if not user.check_twoFAKey(args.get('otp')):
                    return abort(401, "otp code is not valid")

            return jsonify(dict(
                    success=True,
                    token=user.getToken(),
                    data=user.to_json(),
                ))

        return abort(401, 'Wrong username or password')


@api_rest.route('/me')
@api_rest.doc(security='apikey')
class GetMe(SecureResource):
    @api_rest.doc(model=loginData)
    def get(self):
        """ get me info """

        user = User.query.filter(User.email==g.user.email).first()

        if not user:
            return abort(401, 'token is not valid')

        return jsonify(dict(
                    success=True,
                    token=user.getToken(),
                    data=user.to_json(),
                ))

    @api_rest.doc(model=user_files, parser=UserParser)
    def put(self):
        """ update user settings """

        args = UserParser.parse_args()

        user = User.query.filter(User.email==g.user.email).first()
        if not user:
            return abort(401, 'token is not valid')

        user.update_from_dict(args)

        if args.avatar:
            now = datetime.now()
            filename = "{}_{}".format(now.strftime("%d_%m_%Y_%H_%M_%S"), args.avatar.filename)
            filepath ='user_avatar/{}/{}'.format(user.id, filename)
            s3_store_images(args.avatar, filepath)
            user.avatar = filepath
            user.save()

        return jsonify(user.to_json())



@api_rest.route('/register')
class Register(Resource):
    decorators = [limiter.limit("10/hour")]

    @api_rest.doc(parser=RegisterParser, model=loginData)
    def post(self):
        """ register new user """
        from app import app

        args = RegisterParser.parse_args()

        # if not app.config['ALLOW_REGISTRATION'] and not args.get("invite_code", None):
        #     return abort(401, 'Public registration is disabled, Please purchase the invite code!')

        if not (bool(re.match('((?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,30})', args.get("password")))==True):
            return abort(401, 'The password is weak!')

        if User.check_email(args.get("email")):
            return abort(401, 'email address allready exist')

        sms_code = random.randint(111111,999999)

        new_user = User(
            email=args.get("email"),
            password=generate_password_hash(args.get("password")),
            invite_code=args.get("invite_code"),
            sms_code=sms_code,
        )
        new_user.save()

        # TODO: send email to confirm registration.

        return jsonify(dict(
                    success=True,
                    token=new_user.getToken(),
                    data=new_user.to_json()
                ))


@api_rest.route('/validate-phone')
class ValidateSMSCode(SecureResource):
    decorators = [limiter.limit("10/minute")]

    @api_rest.doc(parser=SMSParser, model=loginData)
    def post(self):
        ''' validate phone number '''

        args = SMSParser.parse_args()
        user = User.query.get(g.user.id)

        if user.sms_code == args.get('sms_code'):
            user.sms_code = ""
            user.is_phone_valid = True
            user.save()

            return jsonify(dict(
                    success=True,
                    token=user.getToken(),
                    data=user.to_json()
                ))

        return abort(403, "code not valid")



@api_rest.route('/change-password')
@api_rest.doc(security='apikey')
class ChangePassword(SecureResource):
    @api_rest.doc(parser=ChangePasswordParser)
    def post(self):
        """ change password """
        
        args = ChangePasswordParser.parse_args()
        user = User.query.get(g.user.id)

        if user:
            if not user.verify_password(args.get('password')):
                return abort(401, 'current pass is wrong')

            if args.get("password") == args.get("new_password"):
                return abort(401, 'New password must be different!')
                
            user.password = generate_password_hash(args.get("new_password"))
            user.save()

            # todo: send email to notification password is changed.

            return jsonify(dict(success=True))

        return abort(401, 'current pass is wrong')



@api_rest.route('/forgot-password')
class ForgotPassword(Resource):
    decorators = [limiter.limit("10/hour")]

    @api_rest.doc(parser=ForgotPasswordParser)
    def post(self):
        """ This api need for reset password by email """
        args = ForgotPasswordParser.parse_args()
        user = User.query.filter_by(email=args.get("email")).first()
        if user:
            user.reset_email_code()
            # TODO: send email with reset link
            resetcode=None
            if os.getenv("FLASK_ENV", None) == "development":
                resetcode = user.email_code

            return jsonify(dict(success=True, resetcode=resetcode))

        return abort(404, "email address is not exist")


@api_rest.route('/reset-password')
class ResetPassword(Resource):
    @api_rest.doc(parser=ResetPasswordParser)
    def post(self):
        """ This api need for reset password using email code """
        args = ResetPasswordParser.parse_args()
        user = User.query.filter_by(email=args.get("email")).first()
        if user and user.email_code == args.get("email-code"):
            if len(args.get("newpassword")) < 6:
                abort(400, "newpassword must have 6+ caracters")
            
            user.ChangePassword(args.get("newpassword"))

            # TODO: send email notification password has been changed.
            return jsonify(dict(success=True))

        return abort(404, "email or email-code is not valid")


@api_rest.route('/logout')
@api_rest.doc(security='apikey')
class logout(SecureResource):
    def get(self):
        """ logout session """
        return jsonify(dict(success=True))


@api_rest.route('/twofa')
@api_rest.doc(security='apikey')
class setup_twofa(SecureResource):
    decorators = [limiter.limit("100/hour")]

    def get(self):
        ''' get otp twofa details '''
        user = User.query.get(g.user.id)
        if user:
            return jsonify(dict(
                    twoFAKey=user.twoFAKey,
                    twoFALoggedin=user.twoFALoggedin))

    @api_rest.doc(parser=twofaParser)
    def put(self):
        ''' setup twofa '''
        args = twofaParser.parse_args()
        user = User.query.get(g.user.id)
        if user.check_twoFAKey(args.get("otp")):
            return jsonify(dict(success=True))

        return abort(401, 'otp code is not valid')

    def delete(self):
        ''' disable twofa login '''
        args = twofaParser.parse_args()
        user = User.query.get(g.user.id)
        if user.check_twoFAKey(args.get("otp")):
            user.twoFALoggedin = False
            user.save()
            return jsonify(dict(success=True))
        return abort(401, 'otp code is not valid')





