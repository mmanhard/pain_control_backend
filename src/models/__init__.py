from flask_mongoengine import MongoEngine

from .user import User
from .subentry import SubEntry, MoodSubEntry, MedicationSubEntry, ActivitySubEntry, PainSubEntry
from .entry import Entry
from .body_part import BodyPart

db = MongoEngine()

def init_app(app):
    db.init_app(app)
