# -*- coding: utf-8 -*-
from .db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask import jsonify, make_response, g
from sqlalchemy import ForeignKey, event, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
import pyotp, uuid, json, jwt, pytz
from utils.aws_tools import s3_get_pre_signed, s3_store_images, s3_delete_file


UserType = [
	'client',
	'expert',
]


class User(db.Model, UserMixin):
	__tablename__ = 'users'
	
	id = db.Column('user_id', db.Integer, primary_key=True)
	email = db.Column(db.String(length=250), unique=True, nullable=False)
	password = db.Column(db.String(length=250), nullable=False)
	
	phone = db.Column(db.String(length=100))
	first_name = db.Column(db.String(length=100))
	last_name = db.Column(db.String(length=100))
	city = db.Column(db.String(length=100))
	address = db.Column(db.Text)
	country = db.Column(db.String(50), nullable=True)
	avatar = db.Column(db.String(250), nullable=True)

	title = db.Column(db.String(length=250))
	description = db.Column(db.Text)

	twoFALoggedin = db.Column(db.Boolean, default=False)
	twoFAKey = db.Column(db.String(length=250), nullable=False, default=pyotp.random_base32())
	
	invite_code = db.Column(db.String(length=250))
	email_code = db.Column(db.String(length=250))

	apiKey = db.Column(db.String(length=255), default=pyotp.random_base32())
	emailConfirmed = db.Column(db.Boolean, nullable=False, default=False)
	lastLogin = db.Column(db.String(length=30))
	userIP = db.Column(db.String(length=30))
	
	tz = db.Column(db.String(50), default='UTC', nullable=True)
	is_admin = db.Column(db.Boolean, default=False)
	is_disabled = db.Column(db.Boolean, default=False)
	is_verified = db.Column(db.Boolean, default=False)

	user_type = db.Column(Enum(*UserType), default="client", nullable=False)

	updated_at = db.Column(db.DateTime)
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


	def __str__(self):
		return "{} - {}".format(self.id, self.email)

	def __unicode__(self):
		return "{} - {}".format(self.id, self.email)

	def update_from_dict(self, args):
		for arg, value in args.items():
			if args.get(arg) is not None:
				if arg in ["avatar"]:continue
				try:
					setattr(self, arg, value)
				except:pass

		self.updated_at = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
		self.save()

	@staticmethod
	def CreateNew(email):
		newPassword= "changeme"
		new = User(
			email=email,
			password=generate_password_hash(newPassword, method='sha256'),
		)
		#TODO: send email
		return new

	def save(self):
		db.session.add(self)
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def verify_password(self, password):
		# Do not verify NULL passwords at all
		return (self.password and check_password_hash(self.password, password))

	def ChangePassword(self, newPassword):
		self.password = generate_password_hash(newPassword, method='sha256')
		self.email_code = ""
		self.save()

	def get_avatar_url(self):
		if self.avatar:
			return s3_get_pre_signed(self.avatar)
		return self.avatar

	def check_email(email):
		return User.query.filter_by(email=email).first()

	def reset_email_code(self):
		self.email_code = str(uuid.uuid1())
		self.save()

		#TODO: send email notification

	def check_twoFAKey(self, TFACode):
		if self.twoFAKey and len(self.twoFAKey) == 16:
			totp = pyotp.TOTP(self.twoFAKey)
			if totp.verify(TFACode):
				if not self.twoFALoggedin:
					self.twoFALoggedin = True
					self.save()
				return True
		return False

	def required_security_keys(self):
		for key in self.security_key:
			if key.is_disabled == False:
				return True
		return False

	def getToken(self, r_security_login=False):
		from app import app
		token = jwt.encode({
			'id': self.id,
			'exp': datetime.utcnow() + timedelta(minutes=1440),
			'key': r_security_login},
			app.config['SECRET_KEY'],
			algorithm="HS256",
		)
		return token

	@property
	def total_reviews(self):
		return len(self.reviews)

	@property
	def reviews_total_reads(self):
		return sum([review.views for review in self.reviews])

	@property
	def total_useful(self):
		return len(self.votes)

	def to_json(self):
		return dict(
				id=self.id,
				email=self.email,
				full_name=self.full_name,
				tz=self.tz,
				avatar=self.get_avatar_url(),
				is_admin=self.is_admin,
				updated_at=self.updated_at,
				created_at=self.created_at,
				stats=dict(reviews=self.total_reviews, reads=self.reviews_total_reads, useful=self.total_useful)
			)


class SecurityKey(db.Model):
	__tablename__ = 'security_keys'

	id = db.Column('security_key_id',db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
	credential_id = db.Column(db.String(250), unique=True, nullable=False)
	name = db.Column(db.String(160), unique=False, nullable=False)
	pub_key = db.Column(db.String(65), unique=True, nullable=True)
	sign_count = db.Column(db.Integer, default=0)

	is_disabled = db.Column(db.Boolean, default=False)

	updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	user = db.relationship('User', backref='security_key', foreign_keys=[user_id])

	def __str__(self):
		return str(self.user_id)

	__unicode__ = __str__

	def save(self):
		db.session.add(self)
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def to_json(self):
		return dict(
				id=self.id,
				user_id=self.user_id,
				credential_id=self.credential_id,
				name=self.name,
				pub_key=self.pub_key,
				sign_count=self.sign_count,
		)
