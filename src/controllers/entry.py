from ..models.entry import Entry
import datetime
from mongoengine.queryset.visitor import Q

day_times = {
    'wakeup': (5,8),
    'morning': (8,12),
    'lunch': (12,14),
    'afternoon': (14,18),
    'evening': (18,21),
    'bed_time': (21,24)
}

sortMap = {
    'date': '-date',
    'max_pain': '-stats.high',
    'min_pain': '+stats.low',
    'avg_pain': '-stats.avg'
}

class EntryController():

    @staticmethod
    def serializeEntries(entries):
        serialized_entries = []
        for entry in entries:
            serialized_entries.append(entry.serialize())

        return serialized_entries

    @staticmethod
    def getEntries(user, start_date=None, end_date=None, time_of_day=None, body_part=None, sort_by=None):

        # Add query filters for date range, and specific body part.
        query = Q(user=user)
        if start_date is not None:
            query = query & Q(date__gte=start_date)
        if end_date is not None:
            query = query & Q(date__lte=end_date)
        if body_part is not None:
            query = query & Q(pain_subentries__match={ 'body_part': body_part })

        entries = Entry.objects(query)

        # Sort the entries (in chronological order by default).
        if sort_by is not None and sort_by in sortMap:
            entries  = entries.order_by(sortMap[sort_by])
        else:
            entries  = entries.order_by('-date')

        # Filter out entries by time of day.
        if time_of_day in day_times:
            (start_time, end_time) = day_times[time_of_day]

            entries = [entry for entry in entries if (start_time <= entry.date.hour <= end_time)]

        return entries

    @staticmethod
    def getPainEntries(user, body_part, start_date=None, end_date=None, time_of_day=None):

        entries = EntryController.getEntries(user, start_date, end_date, time_of_day, body_part.id)

        # Extract the date and pain level from subentries with the specified body part.
        pain_entries = []
        for entry in entries:
            pain_entry = { 'date': entry.date }
            for subentry in entry.pain_subentries:
                if (subentry.body_part == body_part):
                    pain_entry['pain_level'] = subentry.pain_level
            pain_entries.append(pain_entry)

        return pain_entries

    @staticmethod
    def getEntryByID(user, eid):
        return Entry.objects(Q(user=user) & Q(pk=eid)).first()