import datetime


def current_time_string():
    timing = str(datetime.datetime.now())
    current_time = timing.split()[1]
    return "[" + current_time + "] "
