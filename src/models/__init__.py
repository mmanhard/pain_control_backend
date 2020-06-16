from flask_mongoengine import MongoEngine

from .blacklist_token import BlacklistToken
from .user import User
from .subentry import SubEntry, MoodSubEntry, MedicationSubEntry, ActivitySubEntry, PainSubEntry
from .entry_stats import EntryStats
from .entry import Entry
from .body_part_stats import BodyPartStats
from .body_part import BodyPart

db = MongoEngine()

def init_app(app):
    db.init_app(app)
