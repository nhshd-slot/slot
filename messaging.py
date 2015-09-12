import sms_generator
import sms_twilio
import db
import config


def broadcast_procedure(procedure, location, duration, doctor):
    message = sms_generator.new_procedure_message(procedure, location, duration, doctor)

    recipients = db.get_all_students()
    print(recipients)

    for recipient in recipients:
        print("Sending SMS")
        print(recipient)
        sms_twilio.send_sms(recipient['phone_number'], config.twilio_number, message)
