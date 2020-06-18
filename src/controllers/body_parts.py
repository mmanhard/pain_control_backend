from ..models.body_part import BodyPart
from mongoengine.queryset.visitor import Q
from .entry import EntryController, day_times
from ..models.entry import Entry
from statistics import mean, stdev, median
import queue

class BodyPartController():

    @staticmethod
    def getBodyPartByID(user, bpid, start_date=None, end_date=None, time_of_day=None, movingWindowSize=10):

        body_part = BodyPart.objects(pk=bpid).first()

        pain_entries = EntryController.getPainEntries(user, body_part, start_date, end_date, time_of_day)

        # Compute stats for each day (entries are already sorted by date).
        current_day_levels = []
        current_day = pain_entries[0]['date'].date()
        calendar_stats = []
        for entry in pain_entries:
            entry_day = entry['date'].date()
            if entry_day != current_day:
                daily_stats = {
                    'date': current_day,
                    'stats': BodyPartController.computeStats(current_day_levels)
                }
                calendar_stats.append(daily_stats)
                current_day = entry_day
                current_day_levels = []
            current_day_levels.append(entry['pain_level'])
        daily_stats = {
            'date': current_day,
            'stats': BodyPartController.computeStats(current_day_levels)
        }
        calendar_stats.append(daily_stats)

        # Compute moving stats (e.g. moving average) using a 10 entry window by default.
        pain_level_queue = queue.Queue()
        moving_stats = []
        for (i, entry) in enumerate(pain_entries):
            if pain_level_queue.qsize() >= movingWindowSize:
                entry_moving_stats = {
                    'date': pain_entries[i - movingWindowSize // 2]['date'],
                    'stats': BodyPartController.computeStats(list(pain_level_queue.queue))
                }
                moving_stats.append(entry_moving_stats)
                pain_level_queue.get()

            pain_level_queue.put(entry['pain_level'])

        # Compute stats for each time of day.
        daytime_stats =  {key:{} for key in day_times.keys()}
        for time_of_day in day_times:
            (start_time, end_time) = day_times[time_of_day]

            daytime_levels = [pain_entry['pain_level'] for pain_entry in pain_entries if (start_time <= pain_entry['date'].hour <= end_time)]
            daytime_stats[time_of_day] = BodyPartController.computeStats(daytime_levels)

        # Compute stats for all entries.
        pain_levels = [pain_entry['pain_level'] for pain_entry in pain_entries]
        total_stats = BodyPartController.computeStats(pain_levels)

        pain_stats = {
            'total': total_stats,
            'calendar': calendar_stats,
            'moving': moving_stats,
            'daytime': daytime_stats
        }

        return (body_part, pain_stats)

    @staticmethod
    def computeStats(pain_levels):
        dev = 0
        if len(pain_levels) == 0:
            return None
        elif len(pain_levels) > 1:
            dev = stdev(pain_levels)
        return {
            'high': max(pain_levels),
            'low': min(pain_levels),
            'mean': mean(pain_levels),
            'median': median(pain_levels),
            'stdev': dev
        }


    # def calculateAverage(body_part, startDate, endDate):