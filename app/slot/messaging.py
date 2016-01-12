import datetime

import app.slot.sms_twilio
from app.slot import db_fieldbook as fieldbook, sms_creator
from bg_worker import conn
from rq import Queue

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
    message = sms_creator.new_procedure_message(procedure, location, duration, doctor, message_ref)

    recipients = fieldbook.get_students()
    print(recipients)

    if demo_mobiles:
        for demo_mobile in demo_mobiles:
            if demo_mobile:
                print("Queuing SMS")
                print(demo_mobile)
                result = q.enqueue(app.slot.sms_twilio.send_sms, demo_mobile, message)

    else:
        for recipient in recipients:
            print("Queuing SMS")
            print(recipient)
            result = q.enqueue(app.slot.sms_twilio.send_sms, recipient['mobile_number'], message)


def request_procedure(mobile, friendly_ref):
    try:
        opportunity = [d for d in list_of_opportunities if d['ref'] == int(friendly_ref)][0]
        opportunity_id = str(opportunity['id'])
        print(str.format("Opportunity ID is {0}", opportunity_id))

        students = fieldbook.get_students()
        print(students)
        int_mobile = int(mobile)
        print(int_mobile)

        if False:
            print("Processing in demo mode so will use partially-redacted mobile number as name")
            student_name = str.format("XXXXX XXX{0}", mobile[-3:])

        else:
            print("Processing in live mode")
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

        result = fieldbook.allocate_opportunity(opportunity_id, student_name)
        print(str.format("Result of database commit was {0}", result))
        this_opportunity = fieldbook.get_opportunity(opportunity_id)
        print(str.format("This opportunity is {0}", this_opportunity))

        if result is False:
            result = q.enqueue(app.slot.sms_twilio.send_sms,
                               mobile,
                               "Sorry - this learning opportunity has been taken by another student. ")

        elif result is True:
            message = str.format("Attend {0} by {1}.\n\n"
                                 "Ask for {2} to complete this procedure.\n\n"
                                 "This learning opportunity has been reserved for you.",
                                 this_opportunity['location'],
                                 datetime.datetime.fromtimestamp(this_opportunity['expiry_time']).strftime("%H:%M"),
                                 this_opportunity['teacher'])

            result = q.enqueue(app.slot.sms_twilio.send_sms,
                               mobile,
                               message)

    except IndexError as e:
        print(e)
        print("Opportunity not found")
        app.slot.sms_twilio.send_sms(mobile, "Sorry - this opportunity is not available.")

    except Exception as e:
        print(e)
