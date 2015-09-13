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

    debug_mode = True