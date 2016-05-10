from twilio.rest import TwilioRestClient
from rq import Queue
from run_worker_all import conn as qconn

import config
from slot import db_fieldbook as fieldbook

client = TwilioRestClient(config.twilio_sid, config.twilio_token)

# Set up RQ queue to add background tasks to
q_db = Queue('db', connection=qconn)


def send_sms(sms_to, sms_body):
    try:
        print("Sending SMS to Twilio API")

        client.messages.create(to=sms_to, from_=config.twilio_number, body=sms_body)

        q_db.enqueue(fieldbook.add_sms_log,
                     config.twilio_number,
                     sms_to,
                     sms_body,
                     "OUT")

        print("SMS sent to Twilio API")

    except Exception as e:
        print(e)
        pass

