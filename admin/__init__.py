from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask import session, redirect, url_for, request, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user
from sqlalchemy import func

class MyAdminIndexView(AdminIndexView):
	def is_accessible(self):
		return (current_user.is_authenticated and current_user.is_admin)

	def inaccessible_callback(self, name, **kwargs):
		if not self.is_accessible():
			if current_user.is_authenticated:
				abort(404)

			return redirect(url_for('auth.login', next=request.url))


class UserView(ModelView):
	pass