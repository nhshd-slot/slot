import datetime

import db_sheets
import sms_generator
import sms_twilio
from rq import Queue
from bg_worker import conn

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


def broadcast_procedure(procedure, location, duration, doctor, ref_id, demo_mobiles=None):
    message_ref = get_friendly_ref(ref_id)
    print(str.format("Ref is {0}", ref_id))
    message = sms_generator.new_procedure_message(procedure, location, duration, doctor, message_ref)

    recipients = db_sheets.get_all_students()
    print(recipients)

    if demo_mobiles:
        for demo_mobile in demo_mobiles:
            if demo_mobile:
                print("Queuing SMS")
                print(demo_mobile)
                result = q.enqueue(sms_twilio.send_sms, demo_mobile, message)

    else:
        for recipient in recipients:
            print("Queuing SMS")
            print(recipient)
            sms_twilio.send_sms(recipient['phone_number'], message)



def request_procedure(mobile, friendly_ref):
    try:
        opportunity = [d for d in list_of_opportunities if d['ref'] == int(friendly_ref)][0]
        opportunity_id = str(opportunity['id'])
        print(str.format("Opportunity ID is {0}", opportunity_id))

        students = db_sheets.get_all_students()
        print(students)
        int_mobile = int(mobile)

        if False:
            print("Processing in demo mode so will use partially-redacted mobile number as name")
            student_name = str.format("XXXXX XXX{0}", mobile[-3:])

        else:
            print("Processing in live mode")
            try:
                student = [d for d in students if d['phone_number'] == int_mobile][0]
                student_name = student['student']
            except:
                student_name = "Unknown Student"

        result = db_sheets.update_opportunity(opportunity_id, student_name)
        print(str.format("Result of database commit was {0}", result))
        this_opportunity = db_sheets.get_opportunity(opportunity_id)
        print(str.format("This opportunity is {0}", this_opportunity))

        if result is False:
            sms_twilio.send_sms(mobile, "Sorry - this learning opportunity has been taken by another student. ")

        elif result is True:
            message = str.format("Attend {0} by {1}.\n\n"
                                 "Ask for {2} to complete this procedure.\n\n"
                                 "This learning opportunity has been reserved for you.",
                                 this_opportunity['location'],
                                 datetime.datetime.fromtimestamp(this_opportunity['expiry_time']).strftime("%H:%M"),
                                 this_opportunity['doctor'])

            sms_twilio.send_sms(mobile, message)

    except IndexError as e:
        print(e)
        print("Opportunity not found")
        sms_twilio.send_sms(mobile, "Sorry - this opportunity is not available.")

    except Exception as e:
        print(e)
