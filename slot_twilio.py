from twilio.rest import TwilioRestClient
import config

client = TwilioRestClient(config.twilio_sid, config.twilio_token)


def send_sms(sms_to, sms_from, sms_body):
    message = client.messages.create(to=sms_to, from_=sms_from, body=sms_body)

