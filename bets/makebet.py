from tempfile import TemporaryDirectory
import flask as f
from bets import bets
import psycopg2

INTERNAL_DB_REGISTER_ERROR = "Database could not register\n Error:{}"

def insert_informs(driverId, raceId, betId):
    f.g.conn.execute("""
                INSERT INTO Informs (betID, driverId, raceId)
                VALUES
                (%s, %s, %s)""", (driverId, raceId, betId))
    
    

def enter_informs_driver(driverName, raceId, betId):
    driverId = next(f.g.conn.execute("""SELECT driverId 
                                        From DrivesFor WHERE name=%s"""), (driverName,))
    insert_informs(driverId, raceId, betId)
...
    
def enter_informs_team(team, raceId, betId):
    for driverId in f.g.conn.execute("""SELECT driverId 
                                     From DrivesFor WHERE teamName=%s""", 
                                     (team,)):
        insert_inform(betId, driverId, raceId)
    


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

@bets.route('/placebet', methods = ['GET','POST']) 
def placebet():
    if f.request.method == 'GET': 
       driver_list = list(f.g.conn.execute("""SELECT driverId,name FROM Driver; """))
       team_list = list(f.g.conn.execute("""SELECT teamNAME FROM Team;  """)) 
       race_list = list(f.g.conn.execute("""SELECT raceID,raceName FROM Races; """))
       return f.render_template('bets/placebet.html', drivers = driver_list, teams = team_list, races = race_list)
    if f.request.method == 'POST':
        try:
            betId = next(f.g.conn.execute(f"""
               INSERT INTO Bet (odds, isOver, place, raceID, teamName, driverId, completed)
               VALUES
               (100, %(isOver)s, %(position)s, %(race)s, %(team)s, %(driver)s, FALSE); 
               INSERT INTO Bids 
               VALUES ({f.g.user['uid']},currval('Bet_betid_seq'), %(betsize)s)
               RETURNING currval('Bet_betid_seq'); 
               """, f.request.form))
            create_informs_ent(f.request.form, betId)
        except psycopg2.errors.UniqueViolation as e: # Have better error handling
            error="Duplicate bet, placing this bet seperately"
        except Exception as e:
           print(e)
           error = INTERNAL_DB_REGISTER_ERROR.format(str(e))
        return f.redirect(f.url_for('bets.mybets/0')) 


        
    
    