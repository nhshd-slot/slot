import logging
from flask import Flask
from flask.ext.cache import Cache

app = Flask(__name__)

app.config.from_object('config')

# Define a Cache for the application and clear it on startup
cache = Cache(app,config={'CACHE_TYPE': 'redis'})

with app.app_context():
    cache.clear()

from app.slot import routes, controller

# Set up logging
log = logging.getLogger('slot')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)
