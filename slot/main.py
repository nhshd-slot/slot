import logging

from flask_cache import Cache
from flask_login import LoginManager
from flask_sslify import SSLify

from slot import app

# Set up logging
log = logging.getLogger('slot')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

app.config.from_object('config')
sslify = SSLify(app, age=300)
cache = Cache(app, config={'CACHE_TYPE': 'redis'})

with app.app_context():
    cache.clear()

from slot.users.views import users_blueprint
from .routes import dashboard, render_new_procedure_form, receive_sms, complete_procedure
import slot.users.controller as user_controller
from . import db_fieldbook as db
from . import error_mailer

error_mailer.initialize_app(app, additional_loggers=['slot'])

# Register blueprints
app.register_blueprint(users_blueprint)

# Initialise flask_login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = "users.login"


@login_manager.user_loader
def load_user(user_id):
    print("Loading user {0}".format(user_id))
    result = user_controller.return_user_instance_or_anonymous(db.get_user(user_id))
    return result
