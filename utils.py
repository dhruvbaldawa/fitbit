from datetime import timedelta


def gen_next_day(start):
    rdate = start
    while True:
        rdate = rdate + timedelta(days=1)
        yield rdate


def gen_previous_day(start):
    rdate = start
    while True:
        rdate = rdate - timedelta(days=1)
        yield rdate
