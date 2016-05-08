import datetime
import logging
from random import shuffle

from rq import Queue

from bg_worker import conn
import db_fieldbook as fieldbook, sms_creator
from sms_twilio import send_sms
from utils import mobile_number_string_to_int

# Get a logger
logger = logging.getLogger('slot')

# Set up RQ queue to add background tasks to
q = Queue(connection=conn)

list_of_opportunities = []


def broadcast_procedure(procedure, location, duration, doctor, ref_id):
    response_code = ref_id
    print(str.format("Ref is {0}", ref_id))
    message = sms_creator.new_procedure_message(procedure, location, duration, doctor, response_code)

    recipients = fieldbook.get_students()
    shuffle(recipients)

    message_count = 0

    for recipient in recipients:
        print("Queuing SMS")
        print(recipient)
        result = q.enqueue(send_sms, recipient['mobile_number'], message)
        message_count += 1

    return message_count, response_code


def request_procedure(response_mobile, response_code):

    try:
        # Convert the mobile number string to an int
        int_mobile_number = mobile_number_string_to_int(response_mobile)
        # Try and retrieve the student details from the database using the mobile number
        student = fieldbook.get_student_if_valid_else_none(int_mobile_number)

        # If we can't find a student matching that mobile number, respond to say we don't know who they are.
        if student is None:
            q.enqueue(send_sms,
                      response_mobile,
                      "Sorry - we don't recognise this mobile number.")

            q.enqueue(fieldbook.add_response,
                      response_code,
                      'Unknown',
                      response_mobile,
                      'NOT_RECOGNISED')
            return

        elif student:
            student_name = student['name']

    except Exception as e:
        logger.error("Error checking student identity", exc_info=True)

    try:
        # Get the status of the offer
        offer = fieldbook.get_offer(response_code)
        offer_expired = fieldbook.is_opportunity_expired(offer['opportunity_id'])

        if offer is None:
            q.enqueue(send_sms,
              response_mobile,
              'Sorry - this opportunity is not available.')

            q.enqueue(fieldbook.add_response,
                      response_code,
                      student_name,
                      response_mobile,
                      'NOT_FOUND')
            return

        elif offer:
            offer_status = offer['status']
            logger.debug('Status of Opportunity is {0}'.format(offer_status))

    except Exception as e:
        logger.error('Error getting the status of the offer', exc_info=True)
        return

    try:
        # If the opportunity has already been allocated, notify the user
        if offer_status == 'ALLOCATED':
            logger.debug("Opportunity is already allocated.")

            # Respond to the user and tell them that the opportunity has gone
            q.enqueue(send_sms,
                      response_mobile,
                      'Sorry - this learning opportunity has been taken by another student.')

            # Add their response to the Responses sheet
            q.enqueue(fieldbook.add_response,
                      offer['opportunity_id'],
                      student_name,
                      response_mobile,
                      'NOT_SUCCESSFUL')

            return

        # If the offer is still free, allocate it to the user and let them know
        elif offer_status == 'UNALLOCATED':
            # Attempt to allocate the opportunity
            result = fieldbook.allocate_opportunity(offer['opportunity_id'], student_name)
            logger.debug("Result of database commit was {0}".format( result))

            this_opportunity = fieldbook.get_opportunity(offer['opportunity_id'])
            logger.debug("This opportunity is {0}".format(this_opportunity))

            message = str.format('Opportunity has been reserved for you.\n\n'
                                 'Attend {0} by {1}.\n\n'
                                 'Ask for {2} to complete this procedure.\n\n',
                                 this_opportunity['location'],
                                 datetime.datetime.fromtimestamp(this_opportunity['expiry_time']).strftime("%H:%M"),
                                 this_opportunity['teacher'])

            # Send a message to the user with confirmation and details of the opportunity
            logger.debug('Notifying user')
            q.enqueue(send_sms,
                      response_mobile,
                      message)

            # Add their response to the Responses sheet
            logger.debug('Adding successful response to database')
            q.enqueue(fieldbook.add_response,
                      offer['opportunity_id'],
                      student_name,
                      response_mobile,
                      'successful')

            # Update the offer status to reflect the fact that it's now been allocated
            patch = {'status': 'ALLOCATED'}
            logger.debug('Updating offer status to ALLOCATED')
            fieldbook.update_record('offers',
                                    offer['id'],
                                    patch)

            return

    except Exception as e:
        logger.error('Error responding to procedure request', exc_info=True)


def request_opt_out(response_mobile):

    try:
        # Convert the mobile number string to an int
        int_mobile_number = mobile_number_string_to_int(response_mobile)
        # Mark the student as inactive
        fieldbook.disable_student(int_mobile_number)

    except Exception as e:
        logger.exception(exc_info=True)


def request_opt_in(response_mobile):

    try:
        # Convert the mobile number string to an int
        int_mobile_number = mobile_number_string_to_int(response_mobile)
        # Mark the student as inactive
        fieldbook.enable_student(int_mobile_number)

    except Exception as e:
        logger.exception(exc_info=True)