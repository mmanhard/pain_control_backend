import json
import mongoengine as me
from .body_part_stats import BodyPartStats

class BodyPart(me.Document):
    name = me.StringField(required=True)
    type = me.StringField(required=True)

    user = me.ReferenceField('User', reverse_delete_rule=me.CASCADE, required=True)
    entries = me.ListField(me.ReferenceField('Entry'))

    location = me.StringField()
    notes = me.StringField(max_length=500)

    stats = me.EmbeddedDocumentField('BodyPartStats')

    def __repr__(self):
        return json.dumps(self.serialize(), sort_keys=True, indent=4)

    def serialize(self, customStats=None):
        return {
            'id': str(self.id),
            'name': self.name,
            'type': self.type,
            'user': str(self.user.id),
            'location': self.location,
            'notes': self.notes,
            'entries': self.getEntryIDs(),
            'stats': customStats
        }

    def getEntryIDs(self):
        all_entries = self.entries
        entryIDs = []
        for entry_ref in all_entries:
            entryIDs.append(str(entry_ref.id))

        return entryIDs