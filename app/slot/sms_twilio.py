import config
from app.slot import db_fieldbook as fieldbook
from twilio.rest import TwilioRestClient

client = TwilioRestClient(config.twilio_sid, config.twilio_token)


def send_sms(sms_to, sms_body):
    try:
        print("Sending SMS to Twilio API")
        client.messages.create(to=sms_to, from_=config.twilio_number, body=sms_body)
        fieldbook.add_sms_log(config.twilio_number, sms_to, sms_body, "OUT")
        print("SMS sent to Twilio API")

    except Exception as e:
        print(e)
        pass

