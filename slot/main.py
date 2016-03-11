import logging

from flask import Flask
from flask_cache import Cache
from flask_login import LoginManager
from flask_sslify import SSLify

# Set up logging
log = logging.getLogger('slot')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

app = Flask(__name__)
app.config.from_object('config')
sslify = SSLify(app, age=300)
cache = Cache(app, config={'CACHE_TYPE': 'redis'})

with app.app_context():
    cache.clear()

from slot.users.views import users_blueprint
from routes import dashboard, render_new_procedure_form, receive_sms, complete_procedure
import slot.users.controller as user_controller
import db_fieldbook as db

app.register_blueprint(users_blueprint)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = "users.login"


@login_manager.user_loader
def load_user(user_id):
    print("Loading user {0}".format(user_id))
    result = user_controller.return_user_instance_or_anonymous(db.get_user(user_id))
    return result
