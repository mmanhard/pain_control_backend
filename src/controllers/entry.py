from ..models.entry import Entry
import datetime
from mongoengine.queryset.visitor import Q
from collections import defaultdict
from statistics import mean
import datetime

day_times = {
    'sleep': (0,5),
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
    def serializeEntries(entries, detail_level='high'):
        serialized_entries = []
        for entry in entries:
            serialized_entries.append(entry.serialize(detail_level=detail_level))

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
        if time_of_day is not None:
            query = query & Q(daytime=time_of_day)

        entries = Entry.objects(query)

        # Sort the entries (in chronological order by default).
        if sort_by is not None and sort_by in sortMap:
            entries  = entries.order_by(sortMap[sort_by])
        else:
            entries  = entries.order_by('-date')

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
    def getPainEntryDict(user, start_date=None, end_date=None, time_of_day=None):

        entries = EntryController.getEntries(user, start_date, end_date, time_of_day)

        painEntryDict = defaultdict(list)
        for entry in entries:
            for subentry in entry.pain_subentries:
                pain_entry = {
                    'date': entry.date,
                    'pain_level': subentry.pain_level
                }
                painEntryDict[subentry.body_part.id].append(pain_entry)

        return painEntryDict

    @staticmethod
    def getEntryByID(user, eid):
        # Get the corresponding entry.
        entry = Entry.objects(Q(user=user) & Q(pk=eid)).first()

        # Get the most recent entry (if it exists) and compare it to the current one.
        most_recent_entry = Entry.objects(Q(date__lt=entry.date)).order_by('-date').first()
        most_recent_comp = EntryController.compareEntries(entry, [most_recent_entry])

        # Get all entries from yesterday (if they exist) and compare them to the current one.
        yesterday_end = datetime.datetime(entry.date.year, entry.date.month, entry.date.day)
        yesterday_begin = yesterday_end - datetime.timedelta(days=1)
        yesterday_entries = Entry.objects(Q(date__gt=yesterday_begin) & Q(date__lt=yesterday_end))
        yesterday_comp = EntryController.compareEntries(entry, yesterday_entries)


        # Get all entries from last week (if they exist) and compare them to the current one.
        last_week_end = yesterday_end - datetime.timedelta(days=6)
        last_week_begin = yesterday_begin - datetime.timedelta(days=6)
        last_week_entries = Entry.objects(Q(date__gt=last_week_begin) & Q(date__lt=last_week_end))
        last_week_comp = EntryController.compareEntries(entry, last_week_entries)

        comparisons = {
            'most_recent': most_recent_comp,
            'yesterday': yesterday_comp,
            'last_week': last_week_comp
        }

        return (entry, comparisons)

    @staticmethod
    def compareEntries(base_entry, other_entries):

        pain_levels = {}
        for pain_entry in base_entry.pain_subentries:
            pain_levels[pain_entry.body_part.id] = pain_entry.pain_level

        # Find
        other_pain_levels = defaultdict(list)
        for entry in other_entries:
            for pain_entry in entry.pain_subentries:
                if pain_entry.body_part.id in pain_levels:
                    other_pain_levels[pain_entry.body_part.id].append(pain_entry.pain_level)

        comparisons = {}
        for (id, other_pain_level) in other_pain_levels.items():
            avg_other = mean(other_pain_level)
            comparisons[str(id)] = pain_levels[id] - avg_other

        return comparisons

    @staticmethod
    def getDaytimeFromDate(date):
        for time_of_day in day_times:
            (start_time, end_time) = day_times[time_of_day]

            if (start_time <= date.hour <= end_time):
                return time_of_day

