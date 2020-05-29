import json
import datetime
import mongoengine as me

class Entry(me.Document):

    user = me.ReferenceField('User', reverse_delete_rule=me.CASCADE, required=True)
    date = me.DateTimeField(required=True, default=datetime.datetime.utcnow)

    notes = me.StringField(max_length=500)

    pain_subentries = me.EmbeddedDocumentListField('PainSubEntry')
    mood_subentry = me.EmbeddedDocumentField('MoodSubEntry')
    medication_subentry = me.EmbeddedDocumentField('MedicationSubEntry')
    activity_subentry = me.EmbeddedDocumentField('ActivitySubEntry')

    def __repr__(self):
        return json.dumps(self.serialize(), sort_keys=True, indent=4)

    def serialize(self):
        pain_serialized = []
        for subentry in self.pain_subentries:
            pain_serialized.append(subentry.serialize())

        return {
            'id': str(self.id),
            'user': str(self.user.id),
            'pain_subentries': pain_serialized,
            'notes': self.notes
        }
