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
    'min_pain': '-stats.low',
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
    def getEntries(user, start_date=None, end_date=None, time_of_day=None, pain_point=None, sort_by=None):

        # Add query filters for date range, and specific body part.
        query = Q(user=user)
        if start_date is not None:
            query = query & Q(date__gte=start_date)
        if end_date is not None:
            query = query & Q(date__lte=end_date)
        if pain_point is not None:
            query = query & Q(pain_subentries__match={ 'body_part': pain_point })

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
    def getEntriesByIDs(user, start_date=None, end_date=None, time_of_day=None):

        query = Q(user=user)
        if start_date is not None:
            query = query & Q(date__gte=start_date)
        if end_date is not None:
            query = query & Q(date__lte=end_date)

        entries = Entry.objects(query).order_by('-date')

        if time_of_day in day_times:
            (start_time, end_time) = day_times[time_of_day]

            entries = [entry for entry in entries if (start_time <= entry.date.hour <= end_time)]

        return entries

    @staticmethod
    def getEntryByID(user, eid):
        return Entry.objects(Q(user=user) & Q(pk=eid)).first()