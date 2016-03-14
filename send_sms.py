from twilio.rest import TwilioRestClient

import config

client = TwilioRestClient(config.twilio_sid, config.twilio_token)

numbers = [
    '+447000000000'
]

sms_message = ("Welcome to SLOT - Supervised Learning Opportunities by Text. "
               "\n\n"
               "The trial period has now started - look out for opportunities!")

def send_sms(sms_to, sms_body):
    try:
        print("Sending SMS to {0}".format(sms_to))
        client.messages.create(to=sms_to, from_=config.twilio_number, body=sms_body)
        print("SMS sent to {0}".format(sms_to))

    except Exception as e:
        print(e)
        pass

for number in numbers:
    send_sms(number, sms_message)
