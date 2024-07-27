import random
import string

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

db = SQLAlchemy()
ma = Marshmallow()


def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'jbvcxdtyuijomk,l'

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)

    from .views import auth, feedback, survey
    app.register_blueprint(auth.bp)
    app.register_blueprint(feedback.bp)
    app.register_blueprint(survey.bp)

    return app
