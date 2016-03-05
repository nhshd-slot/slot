from app import app
from app.slot import controller as con
import config
from auth import requires_auth


@app.route('/')
@app.route('/dashboard')
@requires_auth
def index():
    return con.index()


@app.route('/new', methods=['GET', 'POST'])
@requires_auth
def render_new_procedure_form():
    return con.render_new_procedure_form()


@app.route('/sms', methods=['POST'])
@requires_auth
def receive_sms():
    return con.receive_sms()