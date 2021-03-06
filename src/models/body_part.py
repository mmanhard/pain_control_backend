import json
import mongoengine as me
from .body_part_stats import BodyPartStats

class BodyPart(me.Document):
    name = me.StringField(required=True)

    user = me.ReferenceField('User', reverse_delete_rule=me.CASCADE, required=True)
    entries = me.ListField(me.ReferenceField('Entry', reverse_delete_rule=me.PULL))

    location = me.StringField()
    type = me.StringField()
    notes = me.StringField(max_length=500)

    stats = me.EmbeddedDocumentField('BodyPartStats')

    def __repr__(self):
        return json.dumps(self.serialize(), sort_keys=True, indent=4)

    def serialize(self, customStats=None, detail_level='high'):
        serialized = {
            'id': str(self.id),
            'name': self.name,
            'type': self.type,
            'location': self.location,
        }

        if customStats: serialized['stats'] = customStats

        if detail_level == 'high':
            serialized.update({
                'notes': self.notes,
                'entries': self.getEntryIDs(),
            })

        return serialized

    # Collects the ids of all of the entries where this body part was referenced.
    def getEntryIDs(self):
        all_entries = self.entries
        entryIDs = []
        for entry_ref in all_entries:
            entryIDs.append(str(entry_ref.id))

        return entryIDs