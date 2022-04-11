import flask as f


bets = f.Blueprint('bets', __name__, template_folder='templates/bets')

@bets.route('/mybets')
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


        #match find_type(bet):
        #   case (0, 2):  bet_types['driver_race'].append(bet)
        #   case (0, 3):  bet_types['driver_season'].append(bet)
        #   case (1, 2):  bet_types['team_race'].append(bet)
        #   case (1, 3):  bet_types['driver_season'].append(bet)
    
    return f.render_template('bets/bets.html', **bet_types)
    
    
