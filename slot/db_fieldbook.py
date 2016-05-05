import datetime
import logging

import fieldbook_py
import requests

import config
import slot.utils as utils
from slot.main import cache


logger = logging.getLogger('slot')

# Create an instance of a FieldbookClient using fieldbook_py
fb = fieldbook_py.FieldbookClient(
        config.fieldbook_user,
        config.fieldbook_pass,
        config.fieldbook_url)


def get_sheet_all_records(sheet):
    return fb.get_all_rows(sheet)


def add_record(sheet, new_record):
    result = fb.add_row(sheet, new_record)
    return result


def update_record(sheet, patch_id, patch):
    result = fb.update_row(sheet, patch_id, patch)
    return result


@cache.cached(key_prefix='all_doctors')
def get_doctors():
    return [d['name'] for d in get_sheet_all_records('teachers')]


@cache.cached(key_prefix='all_timeframes')
def get_timeframes():
    return [t['timeframe'] for t in get_sheet_all_records('timeframes')]


@cache.cached(key_prefix='all_locations')
def get_locations():
    return [l['name'] for l in get_sheet_all_records('locations')]


@cache.cached(key_prefix='all_procedures')
def get_procedures():
    return [p['name'] for p in get_sheet_all_records('procedures')]


@cache.cached(key_prefix='all_students')
def get_students():
    return [s for s in get_sheet_all_records('students')]


def get_user(username):
    print('get username')
    """Returns a user dictionary if a user with specified username is present in the database"""
    users = fb.get_all_rows('users', username=username)
    if users:
        print(users)
        user = users[0]
        print(user)
        print(type(user))
        logger.debug("Returning user {0}".format(user))
        return user
    else:
        return None


def get_all_opportunities():
    all_opportunities = get_sheet_all_records('opportunities')

    for opportunity in all_opportunities:
        if opportunity["outcome"] == "ATTENDED":
            opportunity["status"] = "Attended"
        elif opportunity["outcome"] == "NOT_ATTENDED":
            opportunity["status"] = "Not Attended"
        elif opportunity["student"]:
            opportunity["status"] = "Accepted"
        elif utils.to_timestamp(datetime.datetime.utcnow()) > int(opportunity["expiry_time"]):
            opportunity["status"] = "Expired"
        else:
            opportunity["status"] = "Offered"

        opportunity["time"] = datetime.datetime.fromtimestamp(opportunity["time_sent"])

    return all_opportunities


def get_opportunity(opportunity_id):
    logger.debug('Getting opportunity {0}'.format(opportunity_id))
    result = fb.get_row('opportunities',
                        opportunity_id)

    # url = str.format('{0}/{1}/{2}', config.fieldbook_url, 'opportunities', opportunity_id)
    # print(url)
    # request = requests.get(url, auth=(config.fieldbook_user, config.fieldbook_pass))
    # print(request.json())
    return result


def get_offer(opportunity_id):
    """Returns a dictionary representing an offer with a matching ID"""
    try:
        logger.debug('Checking status of opportunity {0}'.format(opportunity_id))
        requests = fb.get_all_rows('offers',
                                  opportunity_id=opportunity_id)
        logger.debug('Opportunity Status: {0}'.format(requests))

        if len(requests) > 0:
            offer = requests[0]
            logger.debug("Found offer with status {0}".format(offer['status']))
            return offer
        else:
            logger.debug("Did not find an offer with this Id")
            return None

    except Exception as e:
        logger.error("Error retrieving opportunity from database", exc_info=True)


def get_student_if_valid_else_none(mobile_number):
    """Returns a dictionary representing a student if a student with a matching mobile number is found"""
    try:
        logger.debug("Searching for student with mobile number {0}".format(mobile_number))
        request = fb.get_all_rows('students',
                                  mobile_number=mobile_number)
        logger.debug(request)

        if request:
            student = request[0]
            logger.debug(student)
            return student
        else:
            logger.debug("Student with matching mobile number not found.")
            return None

    except Exception as e:
        logger.error("Error retrieving student from database", exc_info=True)


def add_opportunity(op):
    print(op)
    new_op = {}

    now = utils.to_timestamp(datetime.datetime.utcnow())

    new_op['teacher'] = op['doctor']
    new_op['skill'] = op['procedure']
    new_op['expiry_time'] = int(now + int(op["duration"]) * 60)
    new_op['time_sent'] = int(now)
    new_op['location'] = op["location"]

    result = add_record('opportunities', new_op)

    new_id = result['id']
    return new_id


def add_response(opportunity_id, student, mobile_number, outcome):
    response = {}

    now = utils.to_timestamp(datetime.datetime.utcnow())

    response['opportunity_id'] = opportunity_id
    response['student'] = student
    response['mobile_number'] = mobile_number
    response['outcome'] = outcome
    response['time_of_response'] = int(now)

    logger.debug(response)

    result = add_record('responses', response)
    print(result)
    return result


def add_offer(ref_id, messages_sent):
    new_offer = {}
    now = utils.ticks_now()

    new_offer['time_sent'] = now
    new_offer['opportunity_id'] = ref_id
    new_offer['no_of_offers_made'] = messages_sent
    new_offer['status'] = 'UNALLOCATED'
    print(new_offer)

    result = fb.add_row('offers', new_offer)
    print(result)
    return result


def add_sms_log(from_number, to_number, body, direction):
    try:
        now = int(utils.to_timestamp(datetime.datetime.utcnow()))

        new_sms_log = {
            'timestamp': now,
            'from': from_number,
            'to': to_number,
            'body': body,
            'direction': direction
        }

        add_record('messages', new_sms_log)

    except Exception as e:
        logger.error("Error adding SMS log", exc_info=True)

    return


def disable_student(mobile_number):
    try:
        # Check that the student exists first
        student = get_student_if_valid_else_none(mobile_number)

        # If the student exists in the database, mark them as inactive
        if student:
            student_id = student['id']
            patch_data = {
                'active': 'false'
            }
            update_record('students',student_id, patch_data)

    except Exception as e:
        logger.exception("Error trying to disable student", exc_info=True)


def enable_student(mobile_number):
    try:
        # Check that the student exists first
        student = get_student_if_valid_else_none(mobile_number)

        # If the student exists in the database, mark them as inactive
        if student:
            student_id = student['id']
            patch_data = {
                'active': 'true'
            }
            update_record('students',student_id, patch_data)

    except Exception as e:
        logger.exception("Error trying to disable student", exc_info=True)


def allocate_opportunity(opportunity_id, student_name):
    logger.debug("Attempting to update opportunity record with allocation")

    now = int(utils.to_timestamp(datetime.datetime.utcnow()))

    opportunity = get_opportunity(opportunity_id)

    if opportunity['student'] is None:
        logger.debug('No student allocated for this opportunity yet')

        patch_object = {
            'student': student_name,
            'accepted_time': now
        }

        update_record('opportunities', opportunity_id, patch_object)

        logger.debug('Record updated')

        return True

    else:
        logger.debug('Student already allocated for this opportunity')
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
