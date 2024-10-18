#!/usr/bin/python3
"""Initialize Flask extensions"""
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_session import Session
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect
import pytz


db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
session = Session()
login_manager = LoginManager()
socketio = SocketIO()
csrf = CSRFProtect()
