import mongoengine as me
import json

class EntryStats(me.EmbeddedDocument):
    high = me.FloatField(default=0.0)
    low = me.FloatField(default=10.0)
    avg = me.FloatField(default=0.0)
    num_body_parts = me.IntField(default=0)

    def __repr__(self):
        return json.dumps(self.serialize(), sort_keys=True, indent=4)

    def serialize(self):
        return {
            'high': str(self.high),
            'low': str(self.low),
            'avg': str(self.avg),
            'num_body_parts': str(self.num_body_parts)
        }