#!/usr/bin/python3
"""init package"""
from flask import Flask
from .config import Config
from .extensions import db, bcrypt, migrate, session, login_manager, socketio, csrf, pytz
from .auth import auth
from .routes import api
from .models import User




def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    session.init_app(app)
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(api, url_prefix='/')

    return app
