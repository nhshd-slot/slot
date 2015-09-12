# 3rd Party Modules
import flask

# Local Modules
import config
import db
import messaging

app = flask.Flask(__name__)


@app.route('/')
@app.route('/dashboard')
def index():

    ops = db.get_all_opportunities()

    for op in ops:
        if op["status"] == "Accepted":
            op["class"] = "success"
        elif op["status"] == "Offered":
            op["class"] = "info"
        elif op["status"] == "Expired":
            op["class"] = "active"

    return flask.render_template('dashboard.html', ops = ops)


@app.route('/new', methods=['GET'])
def render_new_procedure_form():
    return flask.render_template('new_procedure.html')


# Endpoint for new opportunity form submission
@app.route('/new', methods=['POST'])
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

    db.add_opportunity(opportunity)
    messaging.broadcast_procedure(opportunity_procedure,
                                  opportunity_location,
                                  opportunity_duration,
                                  opportunity_doctor)

    print(flask.json.dumps(opportunity))
    return flask.redirect('/dashboard', code=302)


# Endpoint for receiving SMS messages from Twilio
@app.route('/sms', methods=['POST'])
def receive_sms():
    print(str.format("Received SMS: \n"
                     "To: {0}\n"
                     "From: {1}\n"
                     "Body: {2}\n",
                     str(flask.request.form['To']),
                     str(flask.request.form['From']),
                     str(flask.request.form['Body'])))
    return '<Response></Response>'


if __name__ == '__main__':
    app.debug = config.debug_mode
    print(str.format("Debug Mode is: {0}", app.debug))
    app.run(
        host="0.0.0.0",
        port=int("5000")
    )
