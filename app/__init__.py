import logging

# Set up logging
log = logging.getLogger('slot')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

from flask import Flask
from flask.ext.cache import Cache
from flask.ext.login import LoginManager
from app.slot.models import User


app = Flask(__name__)
app.config.from_object('config')
cache = Cache(app,config={'CACHE_TYPE': 'redis'})

login_manager = LoginManager()
login_manager.init_app(app)

with app.app_context():
    cache.clear()

from app.slot import routes, controller
from app.slot.users.views import users_blueprint

app.register_blueprint(users_blueprint)

from app.slot.models import User

login_manager.login_view = "users.login"


@login_manager.user_loader
def load_user(user_id):
    return User('slot', 'test')

