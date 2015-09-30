import os

try:
    from local_config import *

except ImportError:

    twilio_sid = os.environ.get('TWILIO_SID', '')
    twilio_token = os.environ.get('TWILIO_TOKEN', '')
    twilio_number = os.environ.get('TWILIO_NUMBER', '')

    google_client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
    google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')

    google_sheet_key = os.environ.get('GOOGLE_SHEET_KEY', '')

    website_user = os.environ.get('WEBSITE_USER', '')
    website_pass = os.environ.get('WEBSITE_PASS', '')

    # We need the following variables to be boolean so we just check for a value against the environment variable
    # to mean True and then take absence of either a value or the variable to mean False

    demo_mode = bool(os.environ.get('DEMO_MODE', False))

    debug_mode = bool(os.environ.get('DEBUG_MODE', False))