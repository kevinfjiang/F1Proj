import flask as f
from bets import bets
import psycopg2

INTERNAL_DB_REGISTER_ERROR = "Database could not register\n Error:{}"

@bets.route('/mybets/<int:outstanding>', methods = ['GET'])
def mybets(outstanding: int=0):
    if f.g.user['uid'] == -1: return f.redirect(f.url_for('auth.login'))
    if outstanding not in [0,1]: return f.redirect(f.url_for('bets.show_account'))
    c = f.g.conn.execute(f"""
                         SELECT Driver.name, T.teamName, Races.raceName, T.isWon, T.place,  T.season, T.odds, T.wager, T.completed
                         FROM ( SELECT * FROM BIDS NATURAL JOIN BET WHERE uid ={f.g.user['uid']} AND completed='{outstanding}')  AS T
                         INNER JOIN Races
                            ON T.raceId=Races.raceId
                         LEFT Join Driver
                            ON T.driverid=Driver.driverid
                        """)
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

    return f.render_template('bets/bets.html', **bet_types)
  


@bets.route('/placebet', methods = ['GET','POST']) 
def placebet():
    if f.request.method == 'GET': 
       driver_list = list(f.g.conn.execute("""SELECT driverId,name FROM Driver; """))
       team_list = list(f.g.conn.execute("""SELECT teamNAME FROM Team;  """)) 
       race_list = list(f.g.conn.execute("""SELECT raceID,raceName FROM Races; """))
       return f.render_template('bets/placebet.html', drivers = driver_list, teams = team_list, races = race_list)
    if f.request.method == 'POST':
        try:
            f.g.conn.execute(f"""
               INSERT INTO Bet (odds, isWon, place, raceID, teamName, driverId, completed)
               VALUES
               (100, %(isWon)s, %(position)s, %(race)s, %(team)s, %(driver)s, FALSE); 
               INSERT INTO Bids 
               VALUES ({f.g.user['uid']},currval('Bet_betid_seq'), %(betsize)s); 
               """, f.request.form)
        except psycopg2.errors.UniqueViolation as e: # Have better error handling
            error="Duplicate bet, placing this bet seperately"
        except Exception as e:
           print(e)
           error = INTERNAL_DB_REGISTER_ERROR.format(str(e))
        return mybets()  

@bets.route('/account', methods = ['GET'])
def show_account():
    if f.g.user['uid'] == -1: return f.redirect(f.url_for('auth.login'))
    name = list(f.g.conn.execute(f"""SELECT name FROM Member WHERE uid = {f.g.user['uid']}"""))
    committed_balance = list(f.g.conn.execute(f"""SELECT SUM(wager) 
                                                 FROM Bids NATURAL JOIN BET 
                                                 WHERE uid = {f.g.user['uid']} AND completed = FALSE """))
    account_balance = list(f.g.conn.execute(f"""SELECT balance FROM member where uid = {f.g.user['uid']}"""))
    committed_balance = committed_balance[0][0]
    account_balance = account_balance[0][0]
    avail_balance = account_balance - committed_balance
    pl = list(f.g.conn.execute(f"""SELECT SUM(payout) FROM Bids NATURAL JOIN Bet
                                  WHERE uid = {f.g.user['uid']} AND completed = TRUE"""))
    pl = pl[0][0]
    return f.render_template('bets/account.html',name=name,avail=avail_balance,committed=committed_balance,pl=pl)
