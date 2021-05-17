import os
from flask import Flask, send_from_directory, jsonify, make_response, render_template, redirect, url_for
from flask_admin import Admin as AdminPanel
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from admin import MyAdminIndexView, UserView
from models import User, db
from flask_admin.menu import MenuLink
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from flask_mail import Mail, Message
from flask_cors import CORS
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import timeago, datetime
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

cache = Cache(config={'CACHE_TYPE': 'SimpleCache','CACHE_DEFAULT_TIMEOUT' : 600})

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

def create_app():
	app = Flask(__name__)

	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	app.config['SECRET_KEY'] = "dsjakdjhajhdjkshakjjkh"
	app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')

	app.config['MAIL_SERVER']=os.getenv("MAIL_SERVER", 'smtp.mailtrap.io')
	app.config['MAIL_PORT'] = os.getenv("MAIL_PORT", 2525) 
	app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME", "a14e5e70c673ef")
	app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD", "cc07654ee94e04") 
	app.config['MAIL_USE_TLS'] = True
	app.config['MAIL_USE_SSL'] = False
	app.config['MAIL_DEBUG'] = False
	app.config['MAIL_DEFAULT_SENDER'] = 'info@securityagent.app'

	app.config['ALLOW_REGISTRATION'] = os.getenv("ALLOW_REGISTRATION", False)

	app.config['STRIPE_PUBLISHABLE_KEY'] = os.getenv("STRIPE_PUBLISHABLE_KEY")
	app.config['STRIPE_SECRET_KEY'] = os.getenv("STRIPE_SECRET_KEY")
	app.config['STRIPE_WEBHOOK_SECRET'] = os.getenv("STRIPE_WEBHOOK_SECRET")

	app.config['ERROR_404_HELP'] = False

	db.init_app(app)
	migrate = Migrate(app, db)
	mail = Mail(app)

	cors = CORS(app, resources={r"/*": {"origins": "*"}})

	return app

app = create_app()
cache.init_app(app)

if os.getenv('SENTRY_DSN') and not app.debug:
	sentry_sdk.init(
		dsn=os.getenv('SENTRY_DSN'),
		integrations=[FlaskIntegration()],
		traces_sample_rate=1.0
	)

limiter = Limiter(app,
	key_func=get_remote_address,
	default_limits=["5000 per day", "1000 per hour"],
)

# Login Manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


# blueprint for auth routes in our app
from admin.auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from apis import api_bp
app.register_blueprint(api_bp)

from cmds import cmds as cmds_bp
app.register_blueprint(cmds_bp)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.template_filter('timeago')
def fromnow(date):
	return timeago.format(date, datetime.datetime.now())

@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))


if os.getenv('ADMIN_PANEL', True):
	admin_ext = AdminPanel(app, url='/admin', index_view=MyAdminIndexView(), name='admin', template_mode='bootstrap3', endpoint="admin")
	admin_ext.add_view(UserView(User, db.session, endpoint='users', name='Users', category='Users'))
	admin_ext.add_link(MenuLink(name='WEBSITE', url="https://ajutor.app"))


if __name__ == "__main__":
	app.run(debug=True, port=5000)
