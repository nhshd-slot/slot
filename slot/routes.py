from slot import basic_auth
from flask_login import login_required

from slot.main import app
from slot import controller as con


@app.route('/')
@app.route('/dashboard')
@login_required
def index():
    return con.index()


@app.route('/new', methods=['GET', 'POST'])
@login_required
def render_new_procedure_form():
    return con.render_new_procedure_form()


@app.route('/sms', methods=['POST'])
@basic_auth.requires_auth
def receive_sms():
    return con.receive_sms()


@app.route('/complete', methods=['POST'])
@login_required
def complete_procedure():
    return con.complete_procedure()