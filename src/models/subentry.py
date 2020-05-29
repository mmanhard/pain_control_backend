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

    def serialize(self):
        return {
            'body_part': str(self.body_part.id),
            'pain_level': self.pain_level,
            'life_impact': self.life_impact,
            'mood_impact': self.mood_impact,
            'notes': self.notes
        }

class MoodSubEntry(SubEntry):
    medication = me.StringField(required=True)
    med_impact = me.IntField(required=True)

class MedicationSubEntry(SubEntry):
    mood = me.StringField(required=True)
    mood_impact = me.IntField(required=True)

class ActivitySubEntry(SubEntry):
    activity = me.StringField(required=True)
    duration = me.IntField(required=True)
    act_impact = me.IntField(required=True)