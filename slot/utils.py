import datetime
import pytz

this_timezone = pytz.timezone('Europe/London')


def timestamp_to_ticks(dt):
    """Converts a datetime to ticks (seconds since Epoch)"""
    delta = (dt - datetime.datetime(1970, 1, 1))
    ticks = int(delta.total_seconds())
    return ticks


def ticks_to_timestamp(ticks):
    """Converts ticks (seconds since Epoch) to a datetime"""
    delta = datetime.timedelta(seconds=ticks)
    new_timestamp = datetime.datetime(1970, 1, 1) + delta
    return new_timestamp


def ticks_utc_now():
    """Returns the current timestamp in ticks"""
    time_now = datetime.datetime.utcnow()
    ticks = int(timestamp_to_ticks(time_now))
    return ticks


def ticks_local_now():
    time_now = datetime.datetime.now(tz=this_timezone)
    ticks = int(timestamp_to_ticks(time_now))
    return ticks


def ticks_is_later_than_now(ticks):
    now = datetime.datetime.utcnow()
    timestamp = ticks_to_timestamp(ticks)
    is_later = timestamp > now
    return is_later


def mobile_number_string_to_int(mobile_string):
    """Converts mobile numbers from a string to an integer"""
    return int(mobile_string)


def redact_mobile_number(mobile_string):
    """Takes a mobile number as a string, and redacts all but the last 3 digits"""
    return str.format('XXXXX XXX{0}', mobile_string[-3:])