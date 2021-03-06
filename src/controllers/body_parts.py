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

    # Given a user, a body part id and optional parameters, returns the body
    # part along with statistics for the entries that satisfy the parameters.
    @staticmethod
    def getBodyPartByID(user, bpid, start_date=None, end_date=None, time_of_day=None, detail_level='high'):

        body_part = BodyPart.objects(pk=bpid).first()

        pain_entries = EntryController.getPainEntries(user, body_part, start_date, end_date, time_of_day)

        pain_stats = BodyPartController.computeBodyPartStats(body_part, pain_entries, start_date, end_date, time_of_day, detail_level)

        return (body_part, pain_stats)

    # Given a body part, a list of pain entries (i.e. a list of dicts that
    # contain the date, daytime, and pain level) and optional parameters,
    # returns a dict of stats for the body part.
    @staticmethod
    def computeBodyPartStats(body_part, pain_entries, start_date=None, end_date=None, time_of_day=None, detail_level='high', movingWindowSize=3):

        if len(pain_entries) > 0:
            pain_stats = {
                'total': BodyPartController.computeTotalStats(pain_entries),
                'daytime': BodyPartController.computeDaytimeStats(pain_entries),
            }

            if detail_level == 'high':
                calendar_stats = BodyPartController.computeCalendarStats(pain_entries)

                pain_stats.update({
                    'calendar': calendar_stats,
                    'moving': BodyPartController.computeMovingStats(calendar_stats, int(movingWindowSize)),
                    'histogram': BodyPartController.computeHistogram(calendar_stats)
                })
        else:
            pain_stats = {
                'total': [],
                'daytime': []
            }

            if detail_level == 'high':
                pain_stats.update({
                    'calendar': [],
                    'moving': [],
                    'histogram': []
                })

        return pain_stats

    # Given a list of pain entries (see computeBodyPartStats()), returns the
    # stats for all of the entries.
    @staticmethod
    def computeTotalStats(pain_entries):
        pain_levels = [pain_entry['pain_level'] for pain_entry in pain_entries]

        total_stats = BodyPartController.computeStats(pain_levels)

        return total_stats

    # Given a list of pain entries (see computeBodyPartStats()), returns the
    # stats for each time of day.
    @staticmethod
    def computeDaytimeStats(pain_entries):
        daytime_stats =  {key:{} for key in day_times.keys()}
        for time_of_day in day_times:
            daytime_levels = [pain_entry['pain_level'] for pain_entry in pain_entries if (pain_entry['daytime'] == time_of_day)]
            daytime_stats[time_of_day] = BodyPartController.computeStats(daytime_levels)

        return daytime_stats

    # Given a list of pain entries (see computeBodyPartStats()) that are
    # sorted by date, returns the stats for each day.
    @staticmethod
    def computeCalendarStats(pain_entries):
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

        return calendar_stats

    # Given a list of stats for each day (in order of date), returns the
    # moving stats (e.g. moving average) using a 3 day window by default.
    @staticmethod
    def computeMovingStats(calendar_stats, movingWindowSize=3):
        high_queue = queue.Queue()
        low_queue = queue.Queue()
        mean_queue = queue.Queue()
        std_dev_queue = queue.Queue()
        moving_stats = []

        for (i, daily_stat) in enumerate(calendar_stats):
            high_queue.put(daily_stat['stats']['high'])
            low_queue.put(daily_stat['stats']['low'])
            mean_queue.put(daily_stat['stats']['mean'])
            std_dev_queue.put(daily_stat['stats']['stdev'])

            if high_queue.qsize() > movingWindowSize:
                high_queue.get()
                low_queue.get()
                mean_queue.get()
                std_dev_queue.get()

            if high_queue.qsize() == movingWindowSize:
                stats = {
                    'high': mean(list(high_queue.queue)),
                    'low': mean(list(low_queue.queue)),
                    'mean': mean(list(mean_queue.queue)),
                    'stdev': mean(list(std_dev_queue.queue)),
                }
                daily_moving_stats = {
                    'date': calendar_stats[i - movingWindowSize // 2]['date'],
                    'stats': stats
                }
                moving_stats.append(daily_moving_stats)

        return moving_stats

    # Given a list of stats for each day (in order of date), returns the
    # histogram for max, min, median, and mean.
    @staticmethod
    def computeHistogram(calendar_stats):
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

        return histogram

    # Given a list of pain levels, returns a dict containing the max, min, mean,
    # median, stddev, and number of entries.
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

    # Given a pain level and a histogram, adds 1 to the corresponding bucket of
    # the histogram.
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
