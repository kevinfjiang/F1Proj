import flask as f

INTERNAL_DB_REGISTER_ERROR = "Database could not register\n Error:{}"

bets = f.Blueprint('bets', __name__, template_folder='templates/bets')

@bets.route('/mybets', methods = ['GET'])
def mybets():
    if f.g.user['uid'] == -1: return f.redirect(f.url_for('auth.login'))
    c = f.g.conn.execute(f"""
                         SELECT Driver.name, T.teamName, Races.raceName, T.season, T.odds, T.wager, T.isOver
                         FROM (SELECT *
                               FROM (SELECT * 
                                     FROM Bids 
                                     WHERE uid='{f.g.user['uid']-2}'
                                     ) T1 
                                INNER JOIN Bet 
                                    ON T1.betId = Bet.betId
                                ) AS T
                         INNER JOIN Races
                            ON T.raceId=Races.raceId
                         INNER Join Driver
                            ON T.driverid=Driver.driverid
                        """)
    c = f.g.conn.execute(f"""
            SELECT *  FROM BIDS NATURAL JOIN BET WHERE uid='{f.g.user['uid']-2}'
            """)
 
    bet_types = {
        'driver_race': [],
        'driver_season': [],
        'team_race': [],
        'team_season': [],
    }
    find_type = lambda entry: tuple(i for i, val in enumerate(entry[:4]) if val!=None)
    for bet in c:
        bet_type = find_type(bet) 
        if bet_type == (0,2):
            bet_types['driver_race'].append(bet)
        elif bet_type == (0,3):
            bet_types['driver_season'].append(bet)
        elif bet_type == (1,2):
            bet_types['team_race'].append(bet)
        else:
            bet_types['driver_season'].append(bet)

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
            bet = f.request.form
            f.g.conn.execute(f"""
               INSERT INTO Bet (odds, isOver, place, raceID, teamName, driverId, completed)
               VALUES
               (1.0, {bet["isOver"]}, {bet['position']}, {bet['race']},{bet['team']}, {bet['driver']}, FALSE); 
               INSERT INTO Bids 
               VALUES ({f.g.user['uid']-2},currval('Bet_betid_seq'),{bet['betsize']}); 
               """)
        except Exception as e:
           print(e)
           error = INTERNAL_DB_REGISTER_ERROR.format(str(e))
        return mybets()  

