import flask as f
import sqlalchemy
from bets import bets
import datetime
import logging

INTERNAL_DB_REGISTER_ERROR = "Database could not register\n Error:{}"

def insert_informs(betId, raceId, driverId, teamname="null"):
    try:
        f.g.conn.execute("""
                    INSERT INTO Informs (betID, raceId, driverId, teamname)
                    VALUES
                    (%s, %s, %s, %s)""", (betId, raceId, driverId, teamname))
    except Exception as e:
        print(e)
        raise e
        
    

def enter_informs_driver(driverName, raceId, betId):
    driverId = next(f.g.conn.execute("""SELECT driverId 
                                        From DrivesFor WHERE name=%s"""), (driverName,))
    insert_informs(driverId, raceId, betId)
    
def enter_informs_team(team, raceId, betId):
    for driverId in f.g.conn.execute("""SELECT driverId 
                                     From DrivesFor WHERE teamName=%s""", 
                                     (team,)):
        insert_informs(betId, driverId, raceId, team)
    

def create_informs_ent(form, betId):
    if form['team'] != "null":
        for driverId in f.g.conn.execute("""SELECT driverId 
                                     From DrivesFor WHERE teamName=%s""", 
                                     (form['team'],)):
            insert_informs(betId, form['race'], driverId,  form['team'])
    else:
        insert_informs(betId, form['race'], form['driver'])

def check_cash(size:str)->bool:
    committed_balance = list(f.g.conn.execute(f"""SELECT SUM(wager) 
                                                 FROM Bids NATURAL JOIN BET 
                                                 WHERE uid = {f.g.user['uid']} AND completed = FALSE """))
    account_balance = list(f.g.conn.execute(f"""SELECT balance FROM member WHERE uid = {f.g.user['uid']}"""))
    committed_balance = committed_balance[0][0]
    account_balance = account_balance[0][0]
    return account_balance-committed_balance-size>0

def check_prior(race:str)->bool:
    resp = list(f.g.conn.execute("""
                     SELECT stop
                     FROM Races
                     WHERE raceName=%s
                     """, (race,)))
    return len(resp)>0 and resp>=datetime.datetime.now().date()

@bets.route('/placebet', methods = ['GET','POST']) 
def placebet():
    error=None
    driver_list = list(f.g.conn.execute("""SELECT driverId,name FROM Driver ORDER BY name ASC; """))
    team_list = list(f.g.conn.execute("""SELECT teamNAME FROM Team ORDER BY teamName ASC;  """)) 
    race_list = list(f.g.conn.execute("""SELECT raceID,raceName FROM Races WHERE stop > CURRENT_DATE OR stop IS NULL ORDER BY raceID ASC, stop ASC; """))
    if f.request.method == 'GET': 
       return f.render_template('bets/placebet.html', drivers = driver_list, teams = team_list, races = race_list)
    if f.request.method == 'POST':
        if check_prior(f.request.form['race']):
            error="Can't place a bet on a race that passed!"
        elif check_cash(f.request.form['betsize']):
            error="You don't have enough funds, brokeass"
        else:
            try:
                betId = next(f.g.conn.execute(f"""
                INSERT INTO Bet (odds, isOver, place, raceID, teamName, driverId, completed)
                VALUES
                (100, %(isOver)s, %(position)s, %(race)s, null, %(driver)s, FALSE); 
                INSERT INTO Bids (uid, betId, wager)
                VALUES ({f.g.user['uid']}, currval('Bet_betid_seq'), %(betsize)s) 
                RETURNING currval('Bet_betid_seq')
                """, f.request.form))
                create_informs_ent(f.request.form, betId[0])
            except sqlalchemy.exc.IntegrityError:
                logging.log(logging.ERROR, "Repeated keys, double check new race is updated")
                error="Repeated bid error, double check new race is updated"
            except Exception as e:
                error = INTERNAL_DB_REGISTER_ERROR.format(e)
        if not error: return f.redirect(f.url_for('bets.mybets', outstanding=0)) 
        return f.render_template('bets/placebet.html', error=error, drivers = driver_list, teams = team_list, races = race_list)
