import flask as f
auth = f.Blueprint('auth', __name__, template_folder='templates/auth')

from auth.login import *
from auth.payment import *

