import datetime


# Method to convert ticks to a timestamp
def to_timestamp(dt):
    return (dt - datetime.datetime(1970, 1, 1)).total_seconds()

def ticks_now():
    return int(to_timestamp(datetime.datetime.utcnow()))