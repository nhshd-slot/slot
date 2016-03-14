import os
import sys
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import slot
from slot.users import controller as slot_users_controller
from slot.users.models import User
from slot import db_fieldbook
