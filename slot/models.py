from flask_login import UserMixin


class User(UserMixin):
    # proxy for a database of users
    user_database = {"test": ("slot", "test"),
               "live": ("slot", "live")}

    def __init__(self, username, password):
        self.id = username
        self.password = password

    @classmethod
    def get(cls,id):
        return cls.user_database.get(id)