import sms_generator
import sms_twilio
import db


def broadcast_procedure(procedure, location, duration, doctor):
    message = sms_generator.new_procedure_message(procedure, location, duration, doctor)

    recipients = db.get_list_students()

    for recipient in recipients:
        sms_twilio.send_sms(recipient.sms_to, recipient.sms_from, message)
