import flask as f


leaderboard = f.Blueprint('leaderboard', __name__, template_folder='templates/auth')

@leaderboard.route('/leaderboard')
def generate_leaderboard(): 
    error = None
    drive_list = get_driver_leaders()
    team_list = get_team_leaders()
    # remove the username from the session if it is there
    return f.render_template('leaderboard/leaderboard.html', teams=team_list, drivers=drive_list)

def get_driver_leaders()-> list:
    return list(f.g.conn.execute("""
                SELECT T.name, T.nationality, Team.teamName, T.points
                FROM Team
                INNER JOIN (SELECT *
                            FROM DrivesFor 
                            INNER JOIN (SELECT Driver.*, points 
                                        FROM Driver
                                        INNER JOIN (SELECT Competes_Record.driverid, SUM(Competes_Record.points) as points
                                                    FROM Competes_Record
                                                    GROUP BY Competes_Record.driverid
                                        ) AS T3 ON Driver.driverId = T3.driverId
                            ) AS T2 ON T2.driverId = DrivesFor.driverId 
                ) as T ON T.teamName=Team.teamName
                ORDER BY T.points DESC, T.name ASC;
                """))
    
def get_team_leaders()-> list: #TODO
    return list(f.g.conn.execute("""
                    SELECT Team.teamName, Team.country, T.points
                    FROM TEAM 
                    INNER JOIN (SELECT teamName, SUM(T2.points) as points
                                FROM DrivesFor 
                                INNER JOIN (SELECT Competes_Record.driverid, SUM(Competes_Record.points) as points
                                            FROM Competes_Record
                                            GROUP BY Competes_Record.driverid      
                                ) AS T2 ON T2.driverId = DrivesFor.driverId 
                                GROUP BY teamName
                    ) as T ON T.teamName=Team.teamName
                    ORDER BY T.points DESC, Team.teamName ASC;
                """))
