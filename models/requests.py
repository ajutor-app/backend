# -*- coding: utf-8 -*-
from .db import db
from sqlalchemy_utils.types.json import JSONType
from sqlalchemy_utils.types.choice import ChoiceType
from datetime import datetime, timedelta
from . import User


PAYMENT_TYPES = (
	('fixed', 'Fixed'),
	('hourly', 'Hourly')
)

REQUEST_TYPES = (
	('standard', 'Standard'),
	('urgent', 'Urgent')
)

class Request(db.Model):
	__tablename__ = 'requests'

	id = db.Column('request_id', db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

	title = db.Column(db.String(255), nullable=False)
	description = db.Column(db.Text)

	# JSON object containing files data (clodinary and aws key)
	files = db.Column(JSONType, default='{}', nullable=False)

	# buyere request status
	is_published = db.Column(db.Boolean, default=False)

	payment_type = db.Column(ChoiceType(PAYMENT_TYPES), nullable=False)
	request_type = db.Column(ChoiceType(REQUEST_TYPES), nullable=False)

	# Product is approved by admin
	is_approved = db.Column(db.Boolean, default=False, nullable=False)
	not_approved = db.Column(db.Boolean, default=False, nullable=False)
	is_deleted = db.Column(db.Boolean, default=False)
	are_files_checked = db.Column(db.Boolean, default=False)

	updated_at = db.Column(db.DateTime)
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	skills = db.relationship('RequestSkills', backref='request', lazy='dynamic')
	user = db.relationship('User', backref='reports', foreign_keys=[user_id])

	def __str__(self):
		return "{} - {}".format(self.id, self.email)

	def __unicode__(self):
		return "{} - {}".format(self.id, self.email)

	def save(self):
		db.session.add(self)
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def get_skills(self):
		return [item.to_json() for item in self.skills]

	def update_from_dict(self, args):
		for arg, value in args.items():
			if args.get(arg) is not None:
				try:
					setattr(self, arg, value)
				except:pass

		self.updated_at = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
		self.save()

	def to_json(self):
		return dict(
				id=self.id,
				user_id=self.user_id,
				title=self.title,
				description=self.description,
				skills=self.get_skills(),
				files=self.files,
				updated_at=self.updated_at,
				created_at=self.created_at,
		)


class RequestSkills(db.Model):
	__tablename__ = 'request_skill'

	id = db.Column('id', db.Integer, primary_key=True)
	request_id = db.Column(db.Integer, db.ForeignKey('requests.request_id'), nullable=False)
	skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)

	def __repr__(self):
		return '<RequestSkills %r>' % self.id

	def save(self):
		db.session.add(self)
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def to_json(self):
		return dict(
			id=self.id,
			request_id=self.request_id,
			skill_id=self.skill_id,
		)



class RequestFile(db.Model):
	__tablename__ = 'request_files'

	id = db.Column('id', db.Integer, primary_key=True)
	request_id = db.Column(db.Integer, db.ForeignKey('requests.request_id'), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

	filename = db.Column(db.String(255))
	attachment_id = db.Column(db.String(36))

	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	user = db.relationship('User', backref='request_files', foreign_keys=[user_id])

	def __repr__(self):
		return '<RequestUpload %r>' % self.id

	def save(self):
		db.session.add(self)
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	@property
	def url(self):
		return "" # Storage.get_attachment_aws_url(self.attachment_id, self.filename)

	def to_json(self):
		return dict(
			id=self.id,
			filename=self.filename,
			attachment_id=self.attachment_id,
			url=self.url,
			created_at=self.created_at,
		)


class RequestBids(db.Model):
	__tablename__ = 'request_bids'

	id = db.Column('request_bid_id', db.Integer, primary_key=True)
	request_id = db.Column(db.Integer, db.ForeignKey('requests.request_id'), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)

	delivery_time = db.Column(db.Interval)
	price = db.Column(db.Integer(), nullable=False)
	description = db.Column(db.Text)

	updated_at = db.Column(db.DateTime)
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	user = db.relationship('User', backref='request_bids', foreign_keys=[user_id])
	request = db.relationship('Request', backref='request_bids', foreign_keys=[request_id])

	@property
	def expert(self):
		return User.query.get(self.user_id)

	def save(self):
		db.session.add(self)
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def to_dict(self):
		return dict(
			id=self.id,
			request_id=self.request_id,
			user_id=self.user_id,
			delivery_time=self.delivery_time,
			price=self.price,
			description=self.description,
			user=self.user.to_json(),
			updated_at=self.updated_at,
			created_at=self.created_at,
		)



class RequestAward(db.Model):
	__tablename__ = 'request_award'

	REASON_CHANGED_MIND = 'changed_mind'
	REASON_CANNOT_DO_JOB = 'cannot_do_job'
	REASON_NOT_AGREE_ON_PRICE = 'not_agree_on_price'
	REASON_NOT_RESPONDING = 'not_responding'
	REASON_AWARDED_BY_ACCIDENT = 'awarded_by_accident'
	REASON_ANOTHER = 'another'

	REVOKE_REASONS = (
		(REASON_CHANGED_MIND, 'I have changed my mind'),
		(REASON_CANNOT_DO_JOB, 'Expert cannot do the job'),
		(REASON_NOT_AGREE_ON_PRICE, 'We could not agree on price'),
		(REASON_NOT_RESPONDING, 'expert is not responding'),
		(REASON_AWARDED_BY_ACCIDENT, 'Awarded by accident'),
		(REASON_ANOTHER, 'Another reason')
	)

	id = db.Column('id', db.Integer, primary_key=True)
	request_id = db.Column(db.Integer, db.ForeignKey('requests.request_id'), nullable=False)
	request_bid_id = db.Column(db.Integer, db.ForeignKey('request_bids.request_bid_id'), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

	revoked = db.Column(db.Boolean, default=False, nullable=False)
	revoke_reason = db.Column(ChoiceType(REVOKE_REASONS))
	revoke_custom_reason = db.Column(db.Text)

	updated_at = db.Column(db.DateTime)
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	def __repr__(self):
		return '<RequestAward %d>' % self.id

	def to_json(self):
		return dict(
			id=self.id,
			request_id=self.request_id,
			request_bid_id=self.request_bid_id,
			user_id=self.user_id,
			revoked=self.revoked,
			revoke_reason=self.revoke_reason,
			revoke_custom_reason=self.revoke_custom_reason,
			updated_at=self.updated_at,
			created_at=self.created_at,
		)