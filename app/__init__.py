import os

import arrow
from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('://', 'ql://', 1)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    return app


app = create_app()

from app.tracker import tracker_bp as tracker_blueprint

app.register_blueprint(tracker_blueprint)

from app.tracker.models import *

from app.auth import auth_bp as auth_blueprint

app.register_blueprint(auth_blueprint)

from app.auth.models import User


@app.route('/')
def index():
    return redirect(url_for('tracker.index'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.template_filter("humanizedt")
def humanize_datetime(dt):
    if dt:
        return arrow.get(dt, 'Asia/Bangkok').humanize()
    else:
        return None
