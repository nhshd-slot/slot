import datetime
import logging

import app.slot.sms_twilio
from app.slot import db_fieldbook as fieldbook, sms_creator
from bg_worker import conn
from rq import Queue

logger = logging.getLogger('slot')

q = Queue(connection=conn)

list_of_opportunities = []


def get_friendly_ref(id):
    if not list_of_opportunities:
        new_ref = 1
        new_opportunity = dict(id=str(id), ref=new_ref)
        list_of_opportunities.append(new_opportunity)
        print(str.format("New ref is {0}", new_ref))
        print(list_of_opportunities)
        return new_ref

    else:
        temp_list = []
        for opp in list_of_opportunities:
            temp_list.append(opp['ref'])

        new_ref = max(temp_list) + 1
        new_opportunity = dict(id=str(id), ref=new_ref)
        list_of_opportunities.append(new_opportunity)

        print(str.format("New opportunity added {0}", new_opportunity))
        return new_ref


def remove_unique_ref(ref):
    print(str.format("Removing ref {0}", ref))
    list_of_opportunities.pop(str(ref), None)


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
        result = q.enqueue(app.slot.sms_twilio.send_sms, recipient['mobile_number'], message)
        message_count += 1

    return message_count, response_code


def request_procedure(mobile, response_code):
    try:
        offer = fieldbook.get_opportunity_status(response_code)
        logger.debug('Opportunity: {0}'.format(offer))

        students = fieldbook.get_students()
        print(students)
        int_mobile = int(mobile)
        print(int_mobile)

        # student_name = str.format("XXXXX XXX{0}", mobile[-3:])

        try:
            for student in students:
                print(student)
                print(student['mobile_number'])
                if student['mobile_number'] == int_mobile:
                    student_name = student['name']
                    print(student_name)

            if not student_name:
                raise Exception('Student not found')

        except Exception as e:
            print(e)
            student_name = 'Unknown Student'

        result = fieldbook.allocate_opportunity(offer['opportunity_id'], student_name)
        print(str.format("Result of database commit was {0}", result))
        this_opportunity = fieldbook.get_opportunity(offer['opportunity_id'])
        print(str.format("This opportunity is {0}", this_opportunity))

        if result is False:
            q.enqueue(app.slot.sms_twilio.send_sms,
                               mobile,
                               "Sorry - this learning opportunity has been taken by another student. ")

        elif result is True:
            message = str.format("Attend {0} by {1}.\n\n"
                                 "Ask for {2} to complete this procedure.\n\n"
                                 "This learning opportunity has been reserved for you.",
                                 this_opportunity['location'],
                                 datetime.datetime.fromtimestamp(this_opportunity['expiry_time']).strftime("%H:%M"),
                                 this_opportunity['teacher'])

            q.enqueue(app.slot.sms_twilio.send_sms,
                               mobile,
                               message)

    except IndexError as e:
        print(e)
        print("Opportunity not found")
        q.enqueue(app.slot.sms_twilio.send_sms,
                           mobile,
                           "Sorry - this opportunity is not available.")

    except Exception as e:
        print(e)
