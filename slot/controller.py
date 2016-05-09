# 3rd Party Modules
import datetime
import os

from rq import Queue
from bg_worker import conn

from slot import db_fieldbook
from flask import request, redirect, render_template, json

import config
import utils
from slot.main import app
from slot import messaging

# Set up RQ queue to add background tasks to
q = Queue(connection=conn)

def dashboard():
    ops = db_fieldbook.get_all_opportunities()
    for op in ops:
        if op["status"] == "Accepted":
            op["class"] = "success"
        elif op["status"] == "Offered":
            op["class"] = "info"
        elif op["status"] == "Expired":
            op["class"] = "active"
        elif op["status"] == "Attended":
            op["class"] = "active"
        elif op["status"] == "Not Attended":
            op["class"] = "active"
        op["remaining_mins"] = int(int(op["expiry_time"] - utils.timestamp_to_ticks(datetime.datetime.utcnow())) / 60)
    return render_template('dashboard.html',
                           ops=ops,
                           dash_refresh_timeout=config.dash_refresh_timeout,
                           instance_name=config.INSTANCE_NAME)


def render_new_procedure_form():
    if request.method == 'POST':
        print(request.form)
        opportunity_doctor = request.form['doctor']
        opportunity_procedure = request.form['procedure']
        opportunity_location = request.form['location']
        opportunity_duration = request.form['duration']

        opportunity = {
            'doctor': opportunity_doctor,
            'procedure': opportunity_procedure,
            'location': opportunity_location,
            'duration': opportunity_duration
        }

        print(opportunity)
        ref_id = db_fieldbook.add_opportunity(opportunity)

        number_messages_sent, message_ref = messaging.broadcast_procedure(opportunity_procedure,
                                                                          opportunity_location,
                                                                          opportunity_duration,
                                                                          opportunity_doctor,
                                                                          ref_id)

        offer = db_fieldbook.add_offer(ref_id, number_messages_sent)
        print(offer['id'])

        print(json.dumps(opportunity))

        return redirect('/dashboard', code=302)

    else:
        procedures = db_fieldbook.get_procedures()
        locations = db_fieldbook.get_locations()
        timeframes = db_fieldbook.get_timeframes()
        doctors = db_fieldbook.get_doctors()
        return render_template('new_procedure.html', procedures=procedures, locations=locations,
                               timeframes=timeframes, doctors=doctors)


def receive_sms():
    sms = {
        'service_number': str(request.form['To']),
        'mobile': str(request.form['From']),
        'message': str(request.form['Body'])
    }

    # Add a log entry for the received message
    q.enqueue(db_fieldbook.add_sms_log,
              sms['mobile'],
              sms['service_number'],
              sms['message'], 'IN')

    app.logger.debug("Received SMS: \n"
                     "Service Number: {0}\n"
                     "Mobile: {1}\n"
                     "Message: {2}\n".format(
                     sms['service_number'],
                     sms['mobile'],
                     sms['message']))

    # Check the message to see if it is an opt-out request
    if sms['message'].upper() in ['STOP', 'STOPALL', 'UNSUBSCRIBE', 'CANCEL', 'END', 'QUIT']:
        q.enqueue(messaging.request_opt_out,
                  sms['mobile'])
        return '<Response></Response>'

    # And check the message to see if it is an opt-in request
    elif sms['message'].upper() in ['START', 'YES']:
        q.enqueue(messaging.request_opt_in,
                  sms['mobile'])
        return '<Response></Response>'

    # Else assume it is a request for an opportunity
    else:
        # Process the procedure request
        q.enqueue(messaging.request_procedure,
                  sms['mobile'],
                  sms['message'])

        # Return a successful response to Twilio regardless of the outcome of the procedure request
        return '<Response></Response>'


def complete_procedure():

    completed_id = request.form['id']

    if request.form['attended_status'] == "Attended":
        attended_status = True
    else:
        attended_status = False

    print(str(completed_id))
    print(str(attended_status))

    db_fieldbook.complete_opportunity(completed_id, attended_status)
    return redirect('/dashboard', code=302)


if __name__ == '__main__':
    app.debug = config.debug_mode
    port = int(os.environ.get("PORT", 5000))
    print(str.format("Debug Mode is: {0}", app.debug))
    app.run(
        host="0.0.0.0",
        port = port
    )
