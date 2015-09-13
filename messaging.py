import sms_generator
import sms_twilio
import db
import config

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
    message_ref = get_friendly_ref(ref_id)
    message = sms_generator.new_procedure_message(procedure, location, duration, doctor, message_ref)

    recipients = db.get_all_students()
    print(recipients)

    for recipient in recipients:
        print("Sending SMS")
        print(recipient)
        sms_twilio.send_sms(recipient['phone_number'], config.twilio_number, message)


def request_procedure(mobile, friendly_ref):
    print("Requesting procedure")
    print(str.format("Friendly Ref is {0}", friendly_ref))
    print(str.format("Mobile is {0}", mobile))

    try:
        print("Looking for opportunity")
        opportunity = [d for d in list_of_opportunities if d['ref'] == int(friendly_ref)][0]
        print(opportunity)
        opportunity_id = str(opportunity['id'])
        print(str.format("Opportunity ID is {0}", opportunity_id))
        opportunity_still_available = True

        students = db.get_all_students()
        print(students)
        print(str.format("Mobile is {0}", mobile))
        int_mobile = int(mobile)
        print("Searching for student based on mobile number...")
        student = [d for d in students if d['phone_number'] == int_mobile][0]
        print(student)
        student_name = student['student']
        print(str.format("Student name is {0}", student_name))
        db.update_opportunity(opportunity_id, student_name)

    except IndexError as e:
        print(e)
        opportunity_still_available = False
        print("Opportunity no longer available")

    except Exception as e:
        print(e)