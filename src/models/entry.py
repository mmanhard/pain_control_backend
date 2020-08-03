import json
import datetime
import mongoengine as me
from .entry_stats import EntryStats

day_times = {
    'sleep': (0,5),
    'wakeup': (5,8),
    'morning': (8,12),
    'lunch': (12,14),
    'afternoon': (14,18),
    'evening': (18,21),
    'bed_time': (21,24)
}

class Entry(me.Document):

    user = me.ReferenceField('User', reverse_delete_rule=me.CASCADE, required=True)
    date = me.DateTimeField(required=True, default=datetime.datetime.now)
    daytime = me.StringField()

    notes = me.StringField(max_length=500)

    stats =  me.EmbeddedDocumentField('EntryStats')
    pain_subentries = me.EmbeddedDocumentListField('PainSubEntry')

    # Classes to be used for a feature implemented at a later date.
    mood_subentry = me.EmbeddedDocumentField('MoodSubEntry')
    medication_subentry = me.EmbeddedDocumentField('MedicationSubEntry')
    activity_subentry = me.EmbeddedDocumentField('ActivitySubEntry')

    def __repr__(self):
        return json.dumps(self.serialize(), sort_keys=True, indent=4)

    def serialize(self, comparisons=None, detail_level='high'):
        serialized = {
            'id': str(self.id),
            'date': self.date,
            'daytime': self.daytime
        }

        if comparisons: serialized['comparisons'] = comparisons

        if detail_level == 'medium' or 'high':

            # Create the stats object if it does not exist.
            if self.stats is not None:
                stats = self.stats
            else:
                stats = EntryStats()
                stats.update(self.pain_subentries)
                self.stats = stats
                self.save()

            pain_serialized = []
            for subentry in self.pain_subentries:
                pain_serialized.append(subentry.serialize(detail_level))

            serialized.update({
                'pain_subentries': pain_serialized,
                'notes': self.notes,
                'stats': stats.serialize(),
            })

        return serialized

    # Given stats for an entry, creates an entry stats object and saves it to
    # the entry object.
    def create_stats(self, high, low, total, num_pain_subentries):
        if num_pain_subentries <= 0:
            return

        # Create the stats object if it doesn't exist.
        if self.stats is not None:
            stats = self.stats
        else:
            stats = EntryStats()

        stats.high = high
        stats.low = low
        stats.avg = total / num_pain_subentries
        stats.num_body_parts = num_pain_subentries

        self.stats = stats
        self.save()