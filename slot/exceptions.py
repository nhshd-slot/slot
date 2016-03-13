from slot.main import app
import logging
from logging import Formatter

from logging.handlers import SMTPHandler
mail_handler = SMTPHandler(app.config['SMTP_SERVER'],
                           app.config['SMTP_FROM'],
                           [app.config['EXCEPTION_EMAIL_ADDRESS']],
                           'SLOT Exception',
                           credentials=(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD']),
                           secure=())

mail_handler.setFormatter(Formatter('''
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
'''))


mail_handler.setLevel(logging.ERROR)
app.logger.addHandler(mail_handler)
logging.getLogger('slot').addHandler(mail_handler)