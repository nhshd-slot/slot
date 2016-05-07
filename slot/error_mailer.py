import logging
from logging import Formatter

from logging.handlers import SMTPHandler


def initialize_app(flask_app, additional_loggers=None):

    smtp_server = flask_app.config['SMTP_SERVER']
    smtp_port = int(flask_app.config['SMTP_PORT'])
    from_email_address = flask_app.config['SMTP_FROM']
    recipient_list = [flask_app.config['EXCEPTION_EMAIL_ADDRESS']]
    smtp_username = flask_app.config['SMTP_USERNAME']
    smtp_password = flask_app.config['SMTP_PASSWORD']
    instance_name = flask_app.config['INSTANCE_NAME']

    mail_handler = SMTPHandler((smtp_server, smtp_port),
                               from_email_address,
                               recipient_list,
                               'SLOT Exception ({0})'.format(instance_name),
                               credentials=(smtp_username, smtp_password),
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

    # Add the mailhandler to the main Flask logger
    flask_app.logger.addHandler(mail_handler)

    for logger in additional_loggers:
        logging.getLogger(logger).addHandler(mail_handler)

    return
