import json
import mongoengine as me

class Entry(me.Document):

    user = me.ReferenceField('User', reverse_delete_rule=me.CASCADE, required=True)
    notes = me.StringField(max_length=500, required=True)

    def __repr__(self):
        return json.dumps(self.serialize(), sort_keys=True, indent=4)

    def serialize(self):
        return {
            'id': str(self.id),
            'user': str(self.user.id),
            'notes': self.notes
        }

    # def __init__(self, user_id, date, medical_entry, activity_entry, mood_entry, body_part_entries, notes):
    #     self.user_id = user_id
    #     self.date = date
    #     self.medical_entry = medical_entry
    #     self.activity_entry = activity_entry
    #     self.mood_entry = mood_entry
    #     self.body_part_entries = body_part_entries
    #     self.notes = notes

    # def __repr__(self):
    #     return json.dumps(self.serialize())
    #
    # def serialize(self):
    #     return {
    #         'id':self.id,
    # 		'username':self.username,
    # 		'date_joined':self.date_joined,
    #         'birthday': self.birthday,
    #         'hometown': self.hometown,
    #         'email': self.email,
    #         'phone_number': self.phone_number,
    #         'medical_history': self.medical_history,
    #     }
