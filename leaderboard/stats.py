import flask as f 

stats = f.Blueprint('stats',__name__, template_folder = 'templates/statistics')

@stats.route('/stats', methods = ['GET','POST'])
def display_stat(driver = None, team = None, race = None):
    print(driver,team,race)
    driver_list = list(f.g.conn.execute("""SELECT driverId, name FROM Driver;"""))
    team_list = list(f.g.conn.execute("""SELECT teamName FROM Team;"""))
    race_list = list(f.g.conn.execute("""SELECT raceId, raceName FROM Races;"""))

    if f.request.method == 'POST':
        query = f.request.form 
        driver = query['driver']
        team = query['team']
        race = query['race']
        return show_result(driver, team, race) 

    return f.render_template('statistics/stats.html', drivers = driver_list, teams = team_list, races = race_list) 

@stats.route('/stats/results', methods = ['GET'])
def show_result(driver = None, team = None, race = None):
     
    print(driver,team,race)

    if driver != 'NULL':
        driver_rec = list(f.g.conn.execute(f"""SELECT raceName, position, points FROM Competes_Record NATURAL JOIN Races  
                    WHERE driverId = {driver}"""))
        return f.render_template('statistics/statsDisplay.html', driver_rec = driver_rec)

    elif team != 'NULL':
        team_rec = list(f.g.conn.execute(f"""SELECT raceName, position, points FROM Competes_Record NATURAL JOIN Races 
                        WHERE driverId in (SELECT driverId
                                            FROM Driver NATURAL JOIN Drivesfor 
                                            WHERE teamname = {team})""")) 
        print(team_rec)
        return f.render_template('statistics/statsDisplay.html', team_rec = team_rec) 

    elif race != 'NULL':
        race_rec = list(f.g.conn.execute(f"""SELECT driverId, name, position, points FROM Competes_Record NATURAL JOIN Races NATURAL JOIN Driver WHERE raceId = {race}"""))
        return f.render_template('statistics/statsDisplay.html', race_rec = race_rec) 
