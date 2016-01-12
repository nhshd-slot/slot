import requests
import config
import datetime
from flask import json


def to_timestamp(dt):
    return (dt - datetime.datetime(1970, 1, 1)).total_seconds()


def get_sheet_all_records(sheet):
    url = str.format('{0}{1}{2}', config.fieldbook_url, '/', sheet)
    print(url)
    request = requests.get(url,
                           auth=(config.fieldbook_user, config.fieldbook_pass))
    return request.json()


def add_record(sheet, new_record):
    url = str.format('{0}{1}{2}', config.fieldbook_url, '/', sheet)
    print(url)
    request = requests.post(url, auth=(config.fieldbook_user, config.fieldbook_pass), json = new_record)
    print(request.status_code)
    result = json.loads(request.text)
    print(result)
    return result


def update_record(sheet, patch_id, patch):
    url = str.format('{0}/{1}/{2}', config.fieldbook_url, sheet, patch_id)
    print(url)
    request = requests.patch(url, auth=(config.fieldbook_user, config.fieldbook_pass), json = patch)
    print(request.status_code)
    result = json.loads(request.text)
    print(result)
    return result


def get_doctors():
    return [d['name'] for d in get_sheet_all_records('teachers')]


def get_timeframes():
    return [t['timeframe'] for t in get_sheet_all_records('timeframes')]


def get_locations():
    return [l['name'] for l in get_sheet_all_records('locations')]


def get_procedures():
    return [p['name'] for p in get_sheet_all_records('procedures')]


def get_students():
    return [s for s in get_sheet_all_records('students')]


def get_all_opportunities():
    all_opportunities = get_sheet_all_records('opportunities')

    for opportunity in all_opportunities:
        if opportunity["outcome"] == "ATTENDED":
            opportunity["status"] = "Attended"
        elif opportunity["outcome"] == "NOT_ATTENDED":
            opportunity["status"] = "Not Attended"
        elif opportunity["student"]:
            opportunity["status"] = "Accepted"
        elif to_timestamp(datetime.datetime.utcnow()) > int(opportunity["expiry_time"]):
            opportunity["status"] = "Expired"
        else:
            opportunity["status"] = "Offered"

        opportunity["time"] = datetime.datetime.fromtimestamp(opportunity["time_sent"])
    return all_opportunities


def get_opportunity(opportunity_id):
    print('Getting opportunity')
    url = str.format('{0}/{1}/{2}', config.fieldbook_url, 'opportunities', opportunity_id)
    print(url)
    request = requests.get(url, auth=(config.fieldbook_user, config.fieldbook_pass))
    print(request.json())
    return request.json()


def add_opportunity(op):
    print(op)
    new_op = {}

    now = to_timestamp(datetime.datetime.utcnow())

    new_op['teacher'] = op['doctor']
    new_op['skill'] = op['procedure']
    new_op['expiry_time'] = int(now + int(op["duration"]) * 60)
    new_op['time_sent'] = int(now)
    new_op['location'] = op["location"]

    result = add_record('opportunities', new_op)

    new_id = result['id']
    return new_id


def add_sms_log(from_number, to_number, body, direction):
    now = int(to_timestamp(datetime.datetime.utcnow()))

    new_sms_log = {
        'timestamp': now,
        'from': from_number,
        'to': to_number,
        'body': body,
        'direction': direction
    }

    add_record('messages', new_sms_log)

    return


def allocate_opportunity(opportunity_id, student_name):
    now = int(to_timestamp(datetime.datetime.utcnow()))

    opportunity = get_opportunity(opportunity_id)

    if opportunity['student'] is None:

        patch_object = {
            'student': student_name,
            'accepted_time': now
        }

        update_record('opportunities', opportunity_id, patch_object)

        return True

    else:
        return False


def complete_opportunity(opportunity_id, outcome):

    if outcome:
        attended_status = 'ATTENDED'
    else:
        attended_status = 'NOT_ATTENDED'

    patch_object = {
        'outcome': attended_status
    }

    update_record('opportunities', opportunity_id, patch_object)

    return