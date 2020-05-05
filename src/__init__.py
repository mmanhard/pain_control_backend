from flask import Flask
from flask_pymongo import PyMongo
import os

from .routes import auth, users

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        MONGO_URI="mongodb://localhost:27017/pain_control_v1",
    )

    mongo = PyMongo(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)

    return app

