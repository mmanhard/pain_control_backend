import mongoengine as me

class SubEntry(me.EmbeddedDocument):
    notes = me.StringField()

    meta = {'allow_inheritance': True}

    def __repr__(self):
        return self.notes

class PainSubEntry(SubEntry):
    body_part = me.ReferenceField('BodyPart', required=True)
    pain_level = me.IntField(required=True)
    life_impact = me.IntField()
    mood_impact = me.IntField()

    def serialize(self, detail_level='high'):
        serialized = {
            'body_part': {
                'id': str(self.body_part.id),
                'name': self.body_part.name,
                'location': self.body_part.location,
            },
            'pain_level': self.pain_level,
        }

        if detail_level == 'high':
            serialized.update({
                'life_impact': self.life_impact,
                'mood_impact': self.mood_impact,
                'notes': self.notes
            })

        return serialized

# Class to be used for a feature implemented at a later date.
class MoodSubEntry(SubEntry):
    medication = me.StringField(required=True)
    med_impact = me.IntField(required=True)

# Class to be used for a feature implemented at a later date.
class MedicationSubEntry(SubEntry):
    mood = me.StringField(required=True)
    mood_impact = me.IntField(required=True)

# Class to be used for a feature implemented at a later date.
class ActivitySubEntry(SubEntry):
    activity = me.StringField(required=True)
    duration = me.IntField(required=True)
    act_impact = me.IntField(required=True)