from app import app
from app.slot import controller as con
import config
from auth import requires_basic_auth
from flask import render_template
from flask.ext.login import login_required


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
@requires_basic_auth
def receive_sms():
    return con.receive_sms()