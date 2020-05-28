from flask import current_app
import json
import mongoengine as me
import datetime
import jwt

from . import BlacklistToken

class User(me.Document):

    email = me.StringField(required=True)
    first_name = me.StringField(max_length=50, required=True)
    last_name = me.StringField(max_length=50, required=True)
    hash = me.StringField(required=True)
    date_joined = me.DateTimeField(required=True, default=datetime.datetime.utcnow)

    phone = me.StringField(max_length=16)
    birthday = me.StringField()
    hometown = me.StringField(max_length=50)
    medical_history = me.StringField(max_length=1000)

    entries = me.ListField(me.ReferenceField('Entry'))
    body_parts = me.ListField(me.ReferenceField('BodyPart'))
    # typ_medications
    # typ_activities

    def __repr__(self):
        return json.dumps(self.serialize(), indent=4)

    def serialize(self, detail_level='high'):
        serialized = {
            'id': str(self.id),
            'first_name': self.first_name,
            'last_name': self.last_name,
        }

        if detail_level == 'medium' or detail_level == 'high':
            serialized.update({
                'email': self.email,
                'phone': self.phone,
                'date_joined': int((datetime.datetime.utcnow() - self.date_joined).total_seconds()),
            })

        if detail_level == 'high':
            serialized.update({
                'birthday': self.birthday,
                'hometown': self.hometown,
                'medical_history': self.medical_history,
                'entries': self.getEntryIDs(),
                'body_parts': self.getBodyPartIDs()
            })

        return serialized

    def getEntryIDs(self):
        all_entries = self.entries
        entryIDs = []
        for entry_ref in all_entries:
            entryIDs.append(str(entry_ref.id))

        return entryIDs

    def getBodyPartIDs(self):
        all_body_parts = self.body_parts
        body_partIDs = []
        for body_part_ref in all_body_parts:
            body_partIDs.append(str(body_part_ref.id))

        return body_partIDs

    def encodeAuthToken(self):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=604800),
                'iat': datetime.datetime.utcnow(),
                'sub': str(self.id)
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return False, 'Token blacklisted. Please log in again.'
            else:
                return True, payload['sub']
        except jwt.ExpiredSignatureError:
            return False, 'Signature expired.'
        except jwt.InvalidTokenError:
            return False, 'Invalid token.'
        except Exception as e:
            return False, e

    @staticmethod
    def getOptionalUserParams():
        return ['phone', 'birthday', 'hometown', 'medical_history']



