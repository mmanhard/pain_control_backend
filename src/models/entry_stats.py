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

    # Given a list of subentries, will compute the max, min, and average values
    # as well as the number of body parts included with the entry. These will be
    # store in the entry stats model.
    def update(self, subentries):
        pain_total = 0
        pain_min = 10
        pain_max = 0
        for subentry in subentries:
            pain_level = subentry.pain_level

            pain_total += pain_level
            if pain_level < pain_min:
                pain_min = pain_level
            if pain_level > pain_max:
                pain_max = pain_level

        self.high = pain_max
        self.low = pain_min

        if subentries:
            self.avg = pain_total / len(subentries)
        else:
            self.avg = 0
        self.num_body_parts = len(subentries)