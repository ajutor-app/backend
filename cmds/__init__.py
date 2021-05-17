import click
from flask import Blueprint, g
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
import random, json
from lorem_text import lorem
from slugify import slugify


cmds = Blueprint('cmds', __name__)

@cmds.cli.command('setup-demo')
def create():
	db.drop_all()
	db.create_all()

	user = User(
		email="admin@admin.com",
		password=generate_password_hash("admin"),
		is_admin=True,
	)
	user.save()

	print("all task is done!!")

