import gspread
import config
import datetime
import uuid
import httplib
import httplib2
import os

from oauth2client.file import Storage
from oauth2client.client import Credentials

def refresh_access_token():
    creds._do_refresh_request(httplib2.Http().request)

print "Loading DB..."


if os.environ.get("GOOGLE_CREDS", None):
    print "Loading google credentials from environment"
    creds = Credentials.new_from_json(os.environ.get("GOOGLE_CREDS",""))
else:
    print "Loading google credentials from file"
    storage = Storage('credentials-nhshd.dat')
    creds = storage.get()

refresh_access_token()

log_worksheet = None
student_worksheet = None
procedures_worksheet = None
timeframes_worksheet = None
locations_worksheet = None
doctors_worksheet = None

def reconnect():
    global log_worksheet, student_worksheet, procedures_worksheet, timeframes_worksheet, locations_worksheet, doctors_worksheet
    gs = gspread.authorize(creds)
    sheet = gs.open_by_key(config.google_sheet_key)
    log_worksheet = sheet.worksheet("log")
    student_worksheet = sheet.worksheet("students")
    procedures_worksheet = sheet.worksheet("procedures")
    timeframes_worksheet = sheet.worksheet("timeframes")
    locations_worksheet = sheet.worksheet("locations")
    doctors_worksheet = sheet.worksheet("doctors")

reconnect()
print "Complete"

def do_with_retry(f):
    try:
        return f()
    except httplib.BadStatusLine:
        print "Got BadStatusLine. Retrying"
        reconnect()
        return f()

def to_timestamp(dt):
    return (dt - datetime.datetime(1970, 1, 1)).total_seconds()


def get_all_students():
    refresh_access_token()

    def doit():
        return student_worksheet.get_all_records()

    return do_with_retry(doit)



def get_all_opportunities():
    refresh_access_token()

    def f():
        rs = log_worksheet.get_all_records()


        for r in rs:
            if r["outcome"] == "ATTENDED":
                r["status"] = "Attended"
            elif r["outcome"] == "NOT_ATTENDED":
                r["status"] = "Not Attended"
            elif r["student"]:
                r["status"] = "Accepted"
            elif to_timestamp(datetime.datetime.utcnow()) > int(r["expiry_time"]):
                r["status"] = "Expired"
            else:
                r["status"] = "Offered"

            r["time"] = datetime.datetime.fromtimestamp(r["time_sent"])
        return rs

    return do_with_retry(f)


## Call this function with a new opportunity:
# db.add_opportunity({
#        "doctor": "Dr Thing",
#        "procedure":"do thing",
#        "location": "the ward",
#        "duration": 20
#    })
#
# Returns the GUID of the created opportunity
def add_opportunity(op):
    refresh_access_token()

    def f():
        vs = [uuid.uuid4()]

        now = to_timestamp(datetime.datetime.utcnow())
        vs.append(op["doctor"])
        vs.append(now)
        vs.append(op["procedure"])
        vs.append(int(now + int(op["duration"]) * 60))
        vs.append(op["location"])
        log_worksheet.append_row(vs)

        return vs[0]

    return do_with_retry(f)

def get_opportunity(guid):
    refresh_access_token()

    def f():
        ops = get_all_opportunities()

        for op in ops:
            if op["id"] == guid:
                return op

    return do_with_retry(f)



def update_opportunity(guid, student_name):
    refresh_access_token()

    def f():
        ops = get_all_opportunities()

        i = 1
        x = None
        for op in ops:
            i += 1
            if op["id"] == guid:
                x = op
                break

        if x["student"]:
            return False

        log_worksheet.update_cell(i, 7, student_name)
        log_worksheet.update_cell(i, 8, to_timestamp(datetime.datetime.utcnow()))

        return True

    return do_with_retry(f)


def complete_opportunity(guid, attended):
    refresh_access_token()

    def f():
        ops = get_all_opportunities()

        i = 1
        x = None
        for op in ops:
            i += 1
            if op["id"] == guid:
                x = op
                break

        if attended:
            log_worksheet.update_cell(i, 9, "ATTENDED")
        else:
            log_worksheet.update_cell(i, 9, "NOT_ATTENDED")

        return True

    return do_with_retry(f)


def get_procedures():
    refresh_access_token()

    def f():
        return [p['procedure'] for p in procedures_worksheet.get_all_records()]

    return do_with_retry(f)

def get_locations():
    refresh_access_token()

    def f():
        return [l['location'] for l in locations_worksheet.get_all_records()]

    return do_with_retry(f)

def get_timeframes():
    refresh_access_token()

    def f():
        return [t['timeframe'] for t in timeframes_worksheet.get_all_records()]

    return do_with_retry(f)

def get_doctors():
    refresh_access_token()

    def f():
        return [d['doctor'] for d in doctors_worksheet.get_all_records()]

    return do_with_retry(f)