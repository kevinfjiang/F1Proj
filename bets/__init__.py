import flask as f
bets = f.Blueprint('bets', __name__, template_folder='templates/bets')

from bets.payout import *
from bets.makebet import *
from bets.bets import *