from models.db import db
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models.users import User
from flask_login import login_user, logout_user, login_required
from flask_login import current_user, UserMixin, LoginManager
import os, re

auth = Blueprint('auth', __name__)


@auth.route('/auth')
def index():
    return redirect(url_for("auth.login"))

@auth.route('/auth/login')
def login():
    return render_template('_admin/login.html')

@auth.route('/auth/signup')
def signup():
    return render_template('_admin/signup.html')

@auth.route('/auth/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.index'))

@auth.route('/auth/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)

    return redirect(url_for('admin.index'))


@auth.route('/auth/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    # if os.getenv("FLASK_ENV") != "development":
    #     flash('admin registration has beed disabled for production server')
    #     return redirect(url_for('auth.signup'))

    # if not (bool(re.match('((?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,30})', password))==True):
    #     flash('The password is weak!')
    #     return redirect(url_for('auth.signup'))

    user = User.query.filter_by(email=email).first()
    if user:
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    new_user = User(email=email, password=generate_password_hash(password))
    new_user.save()


    return redirect(url_for('auth.login'))