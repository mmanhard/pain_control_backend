from ..models.body_part import BodyPart
from mongoengine.queryset.visitor import Q
from .entry import EntryController, day_times
from ..models.entry import Entry
from statistics import mean, stdev, median
import queue

initial_histogram = {
    'none': 0,
    'low': 0,
    'medium': 0,
    'high': 0,
    'xHigh': 0,
}

histogram_map = {
    'none': (0, 2),
    'low': (2, 4),
    'medium': (4, 6),
    'high': (6, 8),
    'xHigh': (8, 10)
}

class BodyPartController():

    @staticmethod
    def getBodyPartByID(user, bpid, start_date=None, end_date=None, time_of_day=None, movingWindowSize=3):

        body_part = BodyPart.objects(pk=bpid).first()

        pain_entries = EntryController.getPainEntries(user, body_part, start_date, end_date, time_of_day)

        if len(pain_entries) > 0:

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

            # Compute moving stats (e.g. moving average) using a 3 day window by default.
            # Also create histogram for max, min, median, and mean.
            high_queue = queue.Queue()
            low_queue = queue.Queue()
            mean_queue = queue.Queue()
            moving_stats = []
            for (i, daily_stat) in enumerate(calendar_stats):
                high_queue.put(daily_stat['stats']['high'])
                low_queue.put(daily_stat['stats']['low'])
                mean_queue.put(daily_stat['stats']['mean'])

                if high_queue.qsize() > movingWindowSize:
                    high_queue.get()
                    low_queue.get()
                    mean_queue.get()

                if high_queue.qsize() == movingWindowSize:
                    stats = {
                        'high': max(list(high_queue.queue)),
                        'low': min(list(low_queue.queue)),
                        'mean': mean(list(mean_queue.queue)),
                    }
                    daily_moving_stats = {
                        'date': calendar_stats[i - movingWindowSize // 2]['date'],
                        'stats': stats
                    }
                    moving_stats.append(daily_moving_stats)

            # Create histogram for max, min, median, and mean based on daily stats.
            histogram = {
                'high': initial_histogram.copy(),
                'low': initial_histogram.copy(),
                'median': initial_histogram.copy(),
                'mean': initial_histogram.copy(),
                'num_days': len(calendar_stats)
            }
            for daily_stat in calendar_stats:
                stats = daily_stat['stats']
                BodyPartController.addPainLevelToHist(stats['high'], histogram['high'])
                BodyPartController.addPainLevelToHist(stats['low'], histogram['low'])
                BodyPartController.addPainLevelToHist(stats['median'], histogram['median'])
                BodyPartController.addPainLevelToHist(stats['mean'], histogram['mean'])

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
                'daytime': daytime_stats,
                'histogram': histogram
            }
        else:
            pain_stats = None

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
            'stdev': dev,
            'num_entries': len(pain_levels)
        }

    @staticmethod
    def addPainLevelToHist(pain_level, histogram):
        if histogram_map['none'][0] <= pain_level < histogram_map['none'][1]:
            histogram['none'] += 1
        elif histogram_map['low'][0] <= pain_level < histogram_map['low'][1]:
            histogram['low'] += 1
        elif histogram_map['medium'][0] <= pain_level < histogram_map['medium'][1]:
            histogram['medium'] += 1
        elif histogram_map['high'][0] <= pain_level < histogram_map['high'][1]:
            histogram['high'] += 1
        elif histogram_map['xHigh'][0] <= pain_level <= histogram_map['xHigh'][1]:
            histogram['xHigh'] += 1
