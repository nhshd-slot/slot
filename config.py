import os

try:
    from local_config import *

except ImportError:

    INSTANCE_NAME = os.environ.get('INSTANCE_NAME', '')

    TWILIO_SID = os.environ.get('TWILIO_SID', '')
    TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN', '')
    TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER', '')

    FIELDBOOK_USER = os.environ.get('FIELDBOOK_USER', '')
    FIELDBOOK_PASS = os.environ.get('FIELDBOOK_PASS', '')
    FIELDBOOK_URL = os.environ.get('FIELDBOOK_URL', '')

    BASIC_AUTH_USER = os.environ.get('BASIC_AUTH_USER', 'user')
    BASIC_AUTH_PASS = os.environ.get('BASIC_AUTH_PASS', 'pass')

    DASH_REFRESH_TIMEOUT = int(os.environ.get('DASH_REFRESH_TIMEOUT', 60))

    SECRET_KEY = os.environ.get('SECRET_KEY', 'secret_key')
    SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME', 'slot-session')

    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '300'))

    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

    SMTP_SERVER = os.getenv('SMTP_SERVER', '')
    SMTP_PORT = os.getenv('SMTP_PORT', '')
    SMTP_FROM = os.getenv('SMTP_FROM', '')
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    EXCEPTION_EMAIL_ADDRESS = os.getenv('EXCEPTION_EMAIL_ADDRESS', '')

    # We need the following variables to be boolean so we just check for a value against the environment variable
    # to mean True and then take absence of either a value or the variable to mean False

    DEBUG_MODE = bool(os.environ.get('DEBUG_MODE', False))