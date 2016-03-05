# 3rd Party Modules
import datetime
import os

from flask import request, redirect, render_template, json

from app import app
import config
from auth import requires_auth
from app.slot import db_fieldbook, messaging
import utils


def index():
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
        op["remaining_mins"] = int(int(op["expiry_time"] - utils.to_timestamp(datetime.datetime.utcnow())) / 60)
    return render_template('dashboard.html', ops=ops)


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


# Endpoint for receiving SMS messages from Twilio
# @app.route('/sms', methods=['POST'])
# @requires_auth
def receive_sms():

    sms = {
        'service_number': str(request.form['To']),
        'mobile': str(request.form['From']),
        'message': str(request.form['Body'])
    }

    print(str.format("Received SMS: \n"
                     "Service Number: {0}\n"
                     "Mobile: {1}\n"
                     "Message: {2}\n",
                     sms['service_number'],
                     sms['mobile'],
                     sms['message']))

    messaging.request_procedure(sms['mobile'], sms['message'])

    db_fieldbook.add_sms_log(sms['mobile'], sms['service_number'], sms['message'], 'IN')

    return '<Response></Response>'


@app.route('/complete', methods=['POST'])
@requires_auth
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
