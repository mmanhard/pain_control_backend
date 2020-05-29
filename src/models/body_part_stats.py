import mongoengine as me
import json

class BodyPartStats(me.EmbeddedDocument):
    # timing_stats = me.EmbeddedDocumentListField('BodyPartStats')
    high = me.FloatField(default=0.0)
    low = me.FloatField(default=10.0)
    avg = me.FloatField(default=0.0)
    num_entries = me.IntField(default=0)

    def __repr__(self):
        return json.dumps(self.serialize(), sort_keys=True, indent=4)

    def serialize(self):
        return {
            'high': str(self.high),
            'low': str(self.low),
            'avg': str(self.avg),
            'num_entries': str(self.num_entries)
        }

# class TimingStats(me.EmbeddedDocument):
#     time_of_day = me.StringField(required=True)
#     avg = me.FloatField(required=True)