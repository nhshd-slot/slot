# 3rd Party Modules
import flask
import datetime
import os

# Local Modules
import config
import db
import messaging

app = flask.Flask(__name__)

from functools import wraps
from flask import request, Response


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == config.website_user and password == config.website_pass

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/')
@app.route('/dashboard')
@requires_auth
def index():

    ops = db.get_all_opportunities()

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

        op["remaining_mins"] = int(int(op["expiry_time"] - db.to_timestamp(datetime.datetime.utcnow())) / 60)

    return flask.render_template('dashboard.html', ops = ops)


@app.route('/new', methods=['GET'])
@requires_auth
def render_new_procedure_form():
    procedures = db.get_procedures()
    locations = db.get_locations()
    timeframes = db.get_timeframes()
    doctors = db.get_doctors()
    return flask.render_template('new_procedure.html', procedures = procedures, locations = locations, timeframes = timeframes, doctors = doctors)


# Endpoint for new opportunity form submission
@app.route('/new', methods=['POST'])
@requires_auth
def new_opportunity():
    opportunity_doctor = flask.request.form['doctor']
    opportunity_procedure = flask.request.form['procedure']
    opportunity_location = flask.request.form['location']
    opportunity_duration = flask.request.form['duration']

    opportunity = dict({
        'doctor': opportunity_doctor,
        'procedure': opportunity_procedure,
        'location': opportunity_location,
        'duration': opportunity_duration
    })

    ref_id = db.add_opportunity(opportunity)
    messaging.broadcast_procedure(opportunity_procedure,
                                  opportunity_location,
                                  opportunity_duration,
                                  opportunity_doctor,
                                  ref_id)

    print(flask.json.dumps(opportunity))
    return flask.redirect('/dashboard', code=302)


# Endpoint for receiving SMS messages from Twilio
@app.route('/sms', methods=['POST'])
@requires_auth
def receive_sms():

    sms = dict(service_number=str(flask.request.form['To']),
               mobile=str(flask.request.form['From']),
               message=str(flask.request.form['Body']))

    print(str.format("Received SMS: \n"
                     "Service Number: {0}\n"
                     "Mobile: {1}\n"
                     "Message: {2}\n",
                     sms['service_number'],
                     sms['mobile'],
                     sms['message']))

    messaging.request_procedure(sms['mobile'], sms['message'])

    db.log_sms(sms['mobile'], sms['service_number'], sms['message'], 'IN')

    return '<Response></Response>'


@app.route('/complete', methods=['POST'])
@requires_auth
def complete_procedure():

    completed_id = flask.request.form['id']

    if flask.request.form['attended_status'] == "Attended":
        attended_status = True
    else:
        attended_status = False

    print(str(completed_id))
    print(str(attended_status))

    db.complete_opportunity(completed_id, attended_status)
    return flask.redirect('/dashboard', code=302)


if __name__ == '__main__':
    app.debug = config.debug_mode
    port = int(os.environ.get("PORT", 5000))
    print(str.format("Debug Mode is: {0}", app.debug))
    app.run(
        host="0.0.0.0",
        port = port
    )
