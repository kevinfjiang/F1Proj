import flask as f
import sqlalchemy
from bets import bets
import datetime
import logging

INTERNAL_DB_REGISTER_ERROR = "Database could not register\n Error:{}"

def insert_informs(driverId, raceId, betId, teamname="null"):
    f.g.conn.execute("""
                INSERT INTO Informs (betID, driverId, raceId, teamname)
                VALUES
                (%s, %s, %s, %s)""", (driverId, raceId, betId, teamname))
    
    

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
    raceId = next(f.g.conn.execute("""
                     SELECT raceID
                     FROM Races
                     WHERE raceName=%s
                     """, (form['race'],)))
    if form['team']:
        enter_informs_team(form['team'], raceId, betId)
    else:
        enter_informs_driver(form['driver'], raceId, betId)

def check_prior(race:str)->bool:
    resp = next(f.g.conn.execute("""
                     SELECT stop
                     FROM Races
                     WHERE raceName=%s
                     """, (race,)))
    return resp!=None and resp>=datetime.datetime.now().date()

@bets.route('/placebet', methods = ['GET','POST']) 
def placebet():
    error=None
    driver_list = list(f.g.conn.execute("""SELECT driverId,name FROM Driver; """))
    team_list = list(f.g.conn.execute("""SELECT teamNAME FROM Team;  """)) 
    race_list = list(f.g.conn.execute("""SELECT raceID,raceName FROM Races; """))
    if f.request.method == 'GET': 
       return f.render_template('bets/placebet.html', drivers = driver_list, teams = team_list, races = race_list)
    if f.request.method == 'POST':
        if check_prior(f.request.form['race']):
            error="Can't place a bet on a race that passed!"
        else:
            try:
                #TODO CHECK that the bet hasn't expired, super simple check
                f.g.conn.execute(f"""
                INSERT INTO Bet (odds, isOver, place, raceID, teamName, driverId, completed)
                VALUES
                (100, %(isOver)s, %(position)s, %(race)s, %(season)s, %(driver)s, FALSE); 
                INSERT INTO Bids 
                VALUES ({f.g.user['uid']}, currval('Bet_betid_seq'), %(betsize)s) 
                """, f.request.form)
                create_informs_ent(f.request.form, next(f.g.conn.execute("SELECT currval('Bet_betid_seq')")))
            except sqlalchemy.exc.IntegrityError:
                logging.log(logging.ERROR, "Repeated keys, double check new race is updated")
            except Exception as e:
                print(e)
                error = INTERNAL_DB_REGISTER_ERROR.format(e)
        if not error: return f.redirect(f.url_for('bets.mybets', outstanding=0)) 
        return f.render_template('bets/placebet.html', error=error, drivers = driver_list, teams = team_list, races = race_list)


        
    
    