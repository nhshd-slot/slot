import gspread
import config
import datetime
import uuid
import httplib2

from oauth2client.file import Storage

def refresh_access_token():
    creds.refresh(httplib2.Http())
    storage.put(creds)

print "Loading DB..."

storage = Storage('credentials-nhshd.dat')
creds = storage.get()
refresh_access_token()
gs = gspread.authorize(creds)
sheet = gs.open_by_key(config.google_sheet_key)
log_worksheet = sheet.worksheet("log")
student_worksheet = sheet.worksheet("students")
procedures_worksheet = sheet.worksheet("procedures")
timeframes_worksheet = sheet.worksheet("timeframes")
locations_worksheet = sheet.worksheet("locations")
doctors_worksheet = sheet.worksheet("doctors")

print "Complete"


def to_timestamp(dt):
    return (dt - datetime.datetime(1970, 1, 1)).total_seconds()


def get_all_students():
    refresh_access_token()
    return student_worksheet.get_all_records()


def get_all_opportunities():
    refresh_access_token()
    rs = log_worksheet.get_all_records()


    for r in rs:
        if r["outcome"] == "COMPLETED":
            r["status"] = "Completed"
        elif r["student"]:
            r["status"] = "Accepted"
        elif to_timestamp(datetime.datetime.now()) > int(r["expiry_time"]):
            r["status"] = "Expired"
        else:
            r["status"] = "Offered"

        r["time"] = datetime.datetime.fromtimestamp(r["time_sent"])
    return rs


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

    vs = [uuid.uuid4()]

    now = to_timestamp(datetime.datetime.now())
    vs.append(op["doctor"])
    vs.append(now)
    vs.append(op["procedure"])
    vs.append(int(now + int(op["duration"]) * 60))
    vs.append(op["location"])
    log_worksheet.append_row(vs)

    return vs[0]

def get_opportunity(guid):
    refresh_access_token()

    ops = get_all_opportunities()

    for op in ops:
        if op["id"] == guid:
            return op



def update_opportunity(guid, student_name):
    refresh_access_token()

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
    log_worksheet.update_cell(i, 8, to_timestamp(datetime.datetime.now()))

    return True

def complete_opportunity(guid):
    refresh_access_token()

    ops = get_all_opportunities()

    i = 1
    x = None
    for op in ops:
        i += 1
        if op["id"] == guid:
            x = op
            break

    log_worksheet.update_cell(i, 9, "COMPLETED")

    return True


def get_procedures():
    refresh_access_token()
    return [p['procedure'] for p in procedures_worksheet.get_all_records()]

def get_locations():
    refresh_access_token()
    return [l['location'] for l in locations_worksheet.get_all_records()]

def get_timeframes():
    refresh_access_token()
    return [t['timeframe'] for t in timeframes_worksheet.get_all_records()]

def get_doctors():
    refresh_access_token()
    return [d['doctor'] for d in doctors_worksheet.get_all_records()]