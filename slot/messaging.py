import datetime
import logging

from rq import Queue

import slot.sms_twilio
from bg_worker import conn
from slot import db_fieldbook as fieldbook, sms_creator

logger = logging.getLogger('slot')

q = Queue(connection=conn)

list_of_opportunities = []


def broadcast_procedure(procedure, location, duration, doctor, ref_id):
    response_code = ref_id
    print(str.format("Ref is {0}", ref_id))
    message = sms_creator.new_procedure_message(procedure, location, duration, doctor, response_code)

    recipients = fieldbook.get_students()
    print(recipients)

    message_count = 0

    for recipient in recipients:
        print("Queuing SMS")
        print(recipient)
        result = q.enqueue(slot.sms_twilio.send_sms, recipient['mobile_number'], message)
        message_count += 1

    return message_count, response_code


def request_procedure(response_mobile, response_code):
    try:
        offer = fieldbook.get_opportunity_status(response_code)
        logger.debug('Opportunity: {0}'.format(offer))

        students = fieldbook.get_students()
        logger.debug(students)

        int_mobile = mobile_number_string_to_int(response_mobile)
        logger.debug(int_mobile)

        try:
            for student in students:
                logger.debug(student)
                if student['mobile_number'] == int_mobile:
                    student_name = student['name']
                    print(student_name)

            if not student_name:
                raise Exception('Student not found')

        except Exception as e:
            logger.exception('Error retrieving student', exc_info=True)
            student_name = 'Unknown Student'

        result = fieldbook.allocate_opportunity(offer['opportunity_id'], student_name)
        print(str.format("Result of database commit was {0}", result))
        this_opportunity = fieldbook.get_opportunity(offer['opportunity_id'])
        print(str.format("This opportunity is {0}", this_opportunity))

        if result is False:
            q.enqueue(slot.sms_twilio.send_sms,
                      response_mobile,
                               'Sorry - this learning opportunity has been taken by another student.')

        elif result is True:
            message = str.format('Attend {0} by {1}.\n\n'
                                 'Ask for {2} to complete this procedure.\n\n'
                                 "This learning opportunity has been reserved for you.",
                                 this_opportunity['location'],
                                 datetime.datetime.fromtimestamp(this_opportunity['expiry_time']).strftime("%H:%M"),
                                 this_opportunity['teacher'])

            q.enqueue(slot.sms_twilio.send_sms,
                      response_mobile,
                      message)

    except IndexError as e:
        print(e)
        print('Opportunity not found')
        q.enqueue(slot.sms_twilio.send_sms,
                  response_mobile,
                  'Sorry - this opportunity is not available.')

    except Exception as e:
        print(e)


# TODO: Add some extra validation and data-cleansing logic to this
# Converts mobile numbers from strings to integers
def mobile_number_string_to_int(mobile_string):
    return int(mobile_string)


# Takes a mobile number as a string, and redacts all but the last 3 digits
def redact_mobile_number(mobile_string):
    return str.format('XXXXX XXX{0}', mobile_string[-3:])
