import flask as f 
import helper.helper as helper

stats = f.Blueprint('stats', __name__, template_folder = 'templates/statistics')

@stats.route('/stats', methods = ['GET','POST'])
def display_stat(driver = None, team = None, race = None):
    driver_list = list(f.g.conn.execute("""SELECT driverId,name FROM Driver ORDER BY name ASC; """))
    team_list = list(f.g.conn.execute("""SELECT teamNAME FROM Team ORDER BY teamName ASC;  """)) 
    race_list = list(f.g.conn.execute("""SELECT raceID,raceName FROM Races ORDER BY raceID ASC, stop ASC; """))
    if f.request.method == 'POST':
        query = f.request.form 
        driver = query['driver']
        team = query['team']
        race = query['race']
        return show_result(driver, team, race) 

    return helper.render('statistics/stats.html', drivers = driver_list, teams = team_list, races = race_list) 

@stats.route('/stats/results', methods = ['GET'])
def show_result(driver = None, team = None, race = None):
    if driver != 'NULL':
        driver_rec = list(f.g.conn.execute(f"""SELECT raceName, position, points, name FROM Competes_Record NATURAL JOIN Races NATURAL JOIN Driver 
                    WHERE driverId = {driver}"""))
        return helper.render('statistics/statsDisplay.html', driver_rec = driver_rec)

    elif team != 'NULL':
        team_rec = list(f.g.conn.execute(f"""SELECT raceName, name,  position, points FROM Competes_Record NATURAL JOIN Races NATURAL JOIN Driver 
                        WHERE driverId in (SELECT driverId
                                            FROM Driver NATURAL JOIN Drivesfor 
                                            WHERE teamname = {team})""")) 
        return helper.render('statistics/statsDisplay.html', team_rec = team_rec, teamname = team[1:-1]) 

    elif race != 'NULL':
        race_rec = list(f.g.conn.execute(f"""SELECT driverId, name, position, points, racename FROM Competes_Record NATURAL JOIN Races NATURAL JOIN Driver WHERE raceId = {race} ORDER BY position ASC """))
        return helper.render('statistics/statsDisplay.html', race_rec = race_rec) 
