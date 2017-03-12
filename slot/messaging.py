import datetime
import logging
import random

from rq import Queue

from .run_worker_all import conn as qconn
from . import db_fieldbook as fieldbook, sms_creator
from .sms_twilio import send_sms
from .utils import mobile_number_string_to_int

# Get a logger
logger = logging.getLogger('slot')

# Set up RQ queue to add background tasks to
q_request = Queue('request', connection=qconn)
q_sms = Queue('sms', connection=qconn)
q_db = Queue('db', connection=qconn)
q = Queue(connection=qconn)

list_of_opportunities = []


# Takes a list and returns it with the items in a different order
def shuffle_list(list_to_shuffle):

    logger.debug("Shuffling list")
    new_list = random.sample(list_to_shuffle, len(list_to_shuffle))

    return new_list


# Gets a list of active students from the database, randomises the order, and returns the list of students
def get_active_students_shuffled():
    logger.debug("Retrieving Student List")
    students = fieldbook.get_active_students()
    logger.debug("Students list: {0}".format(students))
    recipient_list = shuffle_list(students)
    logger.debug("Shuffled students list: {0}".format(recipient_list))
    return recipient_list


def broadcast_procedure(procedure, location, doctor, ref_id, expiry_time):
    response_code = ref_id
    print(str.format("Ref is {0}", ref_id))
    message = sms_creator.new_procedure_message(procedure, location, expiry_time, doctor, response_code)

    logger.debug("Getting active students in random order")

    recipients = get_active_students_shuffled()

    logger.debug("Students: {0}".format(recipients))

    # Only take the first 50 students from the list to reduce the sample size for each offer
    # recipients = recipients[:50]

    message_count = 0

    for recipient in recipients:
        logger.debug("Queuing SMS")
        logger.debug(recipient)
        q_sms.enqueue(send_sms, recipient['mobile_number'], message)
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
            q_sms.enqueue(send_sms,
                      response_mobile,
                      "Sorry - we don't recognise this mobile number.")

            q_db.enqueue(fieldbook.add_response,
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


        if offer is None:
            q_sms.enqueue(send_sms,
              response_mobile,
              "Sorry - we didn't find an opportunity with this reference.")

            q_db.enqueue(fieldbook.add_response,
                      response_code,
                      student_name,
                      response_mobile,
                      'NOT_FOUND')
            return

        elif offer:

            offer_expired = fieldbook.is_opportunity_expired(offer['opportunity_id'])

            if offer_expired:
                q_sms.enqueue(send_sms,
                          response_mobile,
                          'Sorry - this opportunity has expired.')

                q_db.enqueue(fieldbook.add_response,
                          response_code,
                          student_name,
                          response_mobile,
                          'EXPIRED')
                return

            else:
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
            q_sms.enqueue(send_sms,
                      response_mobile,
                      'Sorry - this learning opportunity has been taken by another student.')

            # Add their response to the Responses sheet
            q_db.enqueue(fieldbook.add_response,
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
            q_sms.enqueue_call(func=send_sms,
                               args=(response_mobile,
                                     message),
                               at_front=True)

            # Add their response to the Responses sheet
            logger.debug('Adding successful response to database')
            q_db.enqueue(fieldbook.add_response,
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