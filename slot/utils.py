import datetime


def to_timestamp(dt):
    """Converts a timestamp to ticks"""
    return (dt - datetime.datetime(1970, 1, 1)).total_seconds()


def ticks_now():
    """Returns the current timestamp in ticks"""
    return int(to_timestamp(datetime.datetime.utcnow()))


def mobile_number_string_to_int(mobile_string):
    """Converts mobile numbers from a string to an integer"""
    return int(mobile_string)


def redact_mobile_number(mobile_string):
    """Takes a mobile number as a string, and redacts all but the last 3 digits"""
    return str.format('XXXXX XXX{0}', mobile_string[-3:])