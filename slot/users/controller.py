import json
from flask_login import AnonymousUserMixin

import slot.db_fieldbook as db
from . import models


def convert_user_dict_to_user_instance(user_dict):
    return models.User(user_dict['username'], user_dict['password'])


def return_user_instance_or_anonymous(thing):
    if type(thing) == type(dict()):
        user_dict = thing
        user_instance = convert_user_dict_to_user_instance(user_dict)
    elif type(thing) == type(json()):
        user_dict = json.loads(thing)
        user_instance = convert_user_dict_to_user_instance(user_dict)
    elif type(thing) == type(models.User()):
        user_instance = thing

    if isinstance(user_instance, models.User):
        return user_instance
    else:
        return AnonymousUserMixin()


def return_user_if_valid_credentials(username, password):
    # Try and retrieve the user from the database using the username - if successful it means the user exists
    user = db.get_user(username)

    if user:
        # Check that the password is correct
        if password == user['password']:
            print('Valid credentials')
            user_instance = return_user_instance_or_anonymous(user)
            if isinstance(user_instance, models.User):
                return user_instance

    else:
        print('Invalid credentials')
        return None
