import os
import logging
import itertools
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pylab


from datetime import datetime
from utils import gen_next_day, setup_logging

sns.set()
plt.switch_backend('Qt4Agg')

ROOT = os.getcwd()
CONFIG_FILE = os.path.join(ROOT, 'config.ini')
DATA_DIR = os.path.join(ROOT, 'data', 'sleep')
DATA_DB_FILE = os.path.join(DATA_DIR, '.db')

FILENAME_TEMPLATE = 'sleep-{date}.json'
DATE_FORMAT = '%Y-%m-%d'
ASLEEP, AWAKE, REALLY_AWAKE, DEFAULT = 1, 2, 3, -1

logger = logging.getLogger(__name__)


def format_date(date):
    return datetime.strftime(date, DATE_FORMAT)


def convert_ts_to_minute(ts):
    hour, minute, seconds = ts.split(':', 2)
    return int(hour) * 60 + int(minute)


def get_minute_data(day):
    filename = FILENAME_TEMPLATE.format(date=format_date(day))
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'r') as f:
        data = json.loads(f.read())

        minute_data = []
        for record in data['sleep']:
            minute_data += record['minuteData']
        return minute_data


def write_to_dataframe(dataframe, day, minute_data):
    for record in minute_data:
        minute = convert_ts_to_minute(record['dateTime'])
        dataframe[minute][format_date(day)] = int(record['value'])


def main():
    start_date = datetime.strptime('2015-02-06', DATE_FORMAT)
    end_date = datetime.strptime('2015-03-21', DATE_FORMAT)
    days = itertools.takewhile(lambda x: x <= end_date,
                               gen_next_day(start_date))

    date_index = pd.date_range(start_date, end_date)
    df = pd.DataFrame(index=date_index, columns=range(24 * 60), dtype='uint8')
    print df.dtypes
    for day in days:
        logger.info('Processing day {}'.format(format_date(day)))
        minute_data = get_minute_data(day)
        write_to_dataframe(df, day, minute_data)

    df = df.fillna(0)
    sns.heatmap(df, xticklabels=False, yticklabels=False,
                linewidths=0)
    # df.plot()
    pylab.show()

if __name__ == '__main__':
    setup_logging(logger, logging.INFO)
    main()
