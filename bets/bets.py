import flask as f
import helper.helper as helper
from bets import bets

INTERNAL_DB_REGISTER_ERROR = "Database could not register\n Error:{}"

@bets.route('/mybets/<int:outstanding>', methods = ['GET'])
def mybets(outstanding: int=0):
    if f.g.user['uid'] == -1: return f.redirect(f.url_for('auth.login'))
    if outstanding not in [0,1]: return f.redirect(f.url_for('bets.show_account'))
    try:
        c = f.g.conn.execute(f"""
                         SELECT Driver.name, T.teamName, Races.raceName, T.isWon, T.isOver, T.place,  T.season, T.odds, T.wager, T.completed
                         FROM ( SELECT * FROM BIDS NATURAL JOIN BET WHERE uid ={f.g.user['uid']} AND completed='{outstanding}')  AS T
                         INNER JOIN Races
                            ON T.raceId=Races.raceId
                         LEFT Join Driver
                            ON T.driverid=Driver.driverid
                        """)
    except Exception:
        pass
    bet_types = {
        'driver_race': [],
        'driver_season': [],
        'team_race': [],
        'team_season': [],
    }
    for bet in c:
        if bet[0] != None:
            bet_types['driver_race'].append(bet)
        else:
            bet_types['team_race'].append(bet)


       # bet_type = find_type(bet) 
       # if bet_type == (0,2):
       #     bet_types['driver_race'].append(bet)
       # elif bet_type == (0,3):
       #     bet_types['driver_season'].append(bet)
       # elif bet_type == (1,2):
       #     bet_types['team_race'].append(bet)
       # else:
       #     bet_types['driver_season'].append(bet)

    return helper.render('bets/bets.html', **bet_types)
  




@bets.route('/account', methods = ['GET'])
def show_account():
    if f.g.user.get('uid', -1) == -1: return f.redirect(f.url_for('auth.login'))
    name = list(f.g.conn.execute(f"""SELECT name FROM Member WHERE uid = {f.g.user['uid']}"""))
    committed_balance = list(f.g.conn.execute(f"""SELECT COALESCE(SUM(wager),0)
                                                 FROM Bids NATURAL JOIN BET 
                                                 WHERE uid = {f.g.user['uid']} AND completed = FALSE """))
    account_balance = list(f.g.conn.execute(f"""SELECT COALESCE(balance,0) FROM member WHERE uid = {f.g.user['uid']}"""))
    committed_balance = committed_balance[0][0]
    account_balance = account_balance[0][0]
    check_none = lambda v: 0 if v==None else v
    avail_balance = check_none(account_balance) - check_none(committed_balance) # This is pretty clever nice

    return helper.render('bets/account.html',name=name,avail=avail_balance,committed=committed_balance)
