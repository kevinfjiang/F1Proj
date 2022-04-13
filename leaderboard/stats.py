import flask as f 

stats = f.Blueprint('stats',__name__, template_folder = 'templates/statistics')

@stats.route('/stats', methods = ['GET','POST'])
def display_stat(driver = None, team = None, race = None):
    driver_list = list(f.g.conn.execute("""SELECT driverId, name FROM Driver;"""))
    team_list = list(f.g.conn.execute("""SELECT teamName FROM Team;"""))
    race_list = list(f.g.conn.execute("""SELECT raceId, raceName FROM Races;"""))
    if driver == None and team == None and race == None:
        return f.render_template('statistics/stats.html', drivers = driver_list, teams = team_list, races = race_list)
    if f.request.method == 'POST':
        query = bet.request.form 
        if query['driver'] != None: return display_stat(driver = query['driver']) 
        elif query['team'] != None: return display_stat(team = query['team'])
        elif query['race'] != None: return display_stat(race = query['race']) 
        else: return f.render_template('statistics/stats.html')
    
    if driver != None:
        driver_rec = list(f.g.conn.execute(f"""SELECT * FROM Competes_Record NATURAL JOIN Races  
                          WHERE driverId = {driver}"""))
        return f.render_template('statistics/stats.html', drivers = driver_list, teams = team_list, races = race_list, driver_rec = driver_rec)

    elif team != None:
        team_rec = list(f.g.conn.execute(f"""SELECT * FROM Competes_Record 
                             WHERE driverId in (SELECT driverId
                                                FROM Driver NATURAL JOIN Drivesfor 
                                                WHERE teamname = {team})"""))    
        return f.render_template('statistics/stats.html', drivers = driver_list, teams = team_list, races = race_list, team_rec = team_rec) 

    elif race != None:
         race_rec = list(f.g.conn.execute(f"""SELECT * FROM Competes_Record NATURAL JOIN Races                                                 WHERE raceId = {race}"""))
         return f.render_template('statistics/stats.html', drivers = driver_list, teams = team_list, races = race_list, race_rec = race_rec) 
