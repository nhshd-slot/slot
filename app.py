import flask

app = flask.Flask(__name__)
print(str.format("Debug Mode is: {0}", app.debug))


@app.route('/')
def index():
    return flask.render_template('dashboard.html')


@app.route('/new')
def new():
    return flask.render_template('new_procedure.html')


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
    app.run(debug=True)
