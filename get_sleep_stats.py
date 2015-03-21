import os
import logging
import ConfigParser
import json

import fitbit

from datetime import datetime, timedelta


ROOT = os.getcwd()
CONFIG_FILE = os.path.join(ROOT, 'config.ini')
DATA_DIR = os.path.join(ROOT, 'data', 'sleep')
DATA_DB_FILE = os.path.join(DATA_DIR, '.db')

FILENAME_TEMPLATE = 'sleep-{date}.json'
DATE_FORMAT = '%Y-%m-%d'

logger = logging.getLogger(__name__)


def format_date(date):
    return datetime.strftime(date, DATE_FORMAT)


def setup_logging(level):
    logging.basicConfig(level=level)


def setup_filesystem():
    if not os.path.exists(DATA_DIR):
        logger.info('DATA_DIR: {} not found. Creating...'.format(DATA_DIR))
        os.makedirs(DATA_DIR)


def update_last_download_date(date_time):
    with open(DATA_DB_FILE, 'w') as f:
        f.write(format_date(date_time))


def get_last_download_date():
    if not os.path.exists(DATA_DB_FILE):
        logger.info('DB does not exist,. Creating...')
        start_date = datetime(2014, 11, 20)  # magic date when I bought Fitbit
        update_last_download_date(start_date)

    with open(DATA_DB_FILE, 'r') as f:
        return datetime.strptime(f.read(), DATE_FORMAT)


def gen_next_day(start):
    rdate = start
    while True:
        rdate = rdate + timedelta(days=1)
        yield rdate


def download_sleep_stats(client, config):
    setup_filesystem()
    last_download_date = get_last_download_date()
    next_day = gen_next_day(last_download_date)

    from_date = next(next_day)
    while from_date <= datetime.today():
        logging.info('Downloading sleep data for {}'
                     .format(format_date(from_date)))
        data = client.get_sleep(from_date)
        # @TODO: add error handling here
        filename = FILENAME_TEMPLATE.format(date=format_date(from_date))
        filepath = os.path.join(DATA_DIR, filename)
        with open(filename, 'w') as f:
            f.write(json.dumps(data))

        update_last_download_date(from_date)
        from_date = next(next_day)


def main():
    config = ConfigParser.SafeConfigParser()
    config.read(CONFIG_FILE)

    client = fitbit.Fitbit(config.get('credentials', 'consumer_key'),
                           config.get('credentials', 'consumer_secret'),
                           resource_owner_key=config.get('credentials',
                                                         'user_key'),
                           resource_owner_secret=config.get('credentials',
                                                            'user_secret'),)
    logger.info('Client connected.')
    download_sleep_stats(client, config)


if __name__ == '__main__':
    setup_logging(logging.INFO)
    main()
