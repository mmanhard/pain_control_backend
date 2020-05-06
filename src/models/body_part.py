import json
import mongoengine as me

class BodyPart(me.Document):
    name = me.StringField(required=True)
    type = me.StringField(required=True)

    user = me.ReferenceField('User', reverse_delete_rule=me.CASCADE, required=True)
    entries = me.ListField(me.ReferenceField('PainSubEntry'))
    notes = me.StringField(max_length=500)

    def __repr__(self):
        return json.dumps(self.serialize(), sort_keys=True, indent=4)

    def serialize(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'type': self.type,
            'user': str(self.user.id),
            'notes': self.notes
        }
