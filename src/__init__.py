from flask import Flask
from flask_mongoengine import MongoEngine
import os
from mongoengine import *

from .routes import auth, users, entries
from .models.user import User
from .models.entry import Entry

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # app.config.['SEC'](
    #     SECRET_KEY='dev'
    # )

    app.config['MONGODB_SETTINGS'] = {
        'db': 'test2',
        'host': 'mongodb://localhost:27017/pain_control_v1'
    }

    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(entries.bp)

    return app

app = create_app()
db = MongoEngine(app)

# test = User.objects()
# for user in test:
#     user.delete()