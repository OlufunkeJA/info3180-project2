import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager

from .config import Config

app = Flask(__name__)
app.config.from_object(Config)


db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

# Allow Vue frontend to communicate with Flask backend
CORS(app, supports_credentials=True)

# Ensure uploads folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Import models and register blueprints
# Models expect `login_manager` to be available from the `app` package,
# so create/init the manager above before importing models.
from app import models
from app.routes import register_blueprints

register_blueprints(app)
