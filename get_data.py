import requests
import pandas as pd 
import xml.etree.ElementTree as ET
import unidecode
import numpy as np
import sqlalchemy
import logging
import os
DB_USER = os.getenv('user')
DB_PASSWORD = os.getenv('password')

DB_SERVER = 'w411.cisxo9blonu.us-east-1.rds.amazonaws.com' 

url = "http://ergast.com/api/f1/current/last/results" 



payload={}
headers = {}
response = requests.request("GET", url, headers=headers, data=payload, stream=True)
response.raw.decode_content = True


p={}
for event, elem in ET.iterparse(response.raw):
    p.setdefault(elem.tag.split('}')[1], []).append(elem.text)

driver_data, race_data = {}, {}
for col, val in p.items():
    if len(val)==20:
        driver_data[col]=val
    elif len(val)==1:
        race_data[col]=val[0]
df = pd.DataFrame.from_dict(driver_data)
df['name'] = df.apply(lambda row: unidecode.unidecode(f"{row['GivenName']} {row['FamilyName']}"), axis=1)
df['place'] = np.arange(1, len(df) + 1)
points_dict = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
df['points'] = df['place'].apply(lambda pl: points_dict.get(pl, 0))
df = df[['place','name', 'points']]
    

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

# This line creates a database engine that knows how to connect to the URI above
engine = sqlalchemy.create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/proj1part2")
c = engine.connect()
df.to_sql('temp_positions', con=c, if_exists='replace')

raceId = next(c.execute("""UPDATE RACES
                           SET stop=%s
                           WHERE raceName=%s
                           AND season=%s
                           RETURNING raceId""", (race_data['Date'], race_data['RaceName'], race_data['Date'].split('-')[0])))[0]

logging.log(logging.INFO, f"Addding latest race{race_data['RaceName']} {race_data['Date'].split('-')[0]} data to table")
try:
    c.execute("""
          INSERT INTO Competes_Record
          (driverID, raceID, position, points)
          SELECT Driver.driverID, %s, temp_positions.place, temp_positions.points
          FROM temp_positions
          INNER JOIN Driver
            ON Driver.name=temp_positions.name
          """, (raceId,))
except sqlalchemy.exc.IntegrityError:
    logging.log(logging.INFO, "Repeated keys, double check new race is updated")
except Exception as e:
    logging.log(logging.WARN, f"Internal DB Error: {e}")


logging.log(logging.INFO, f"Addding latest race{race_data['RaceName']} {race_data['Date'].split('-')[0]} data to table")
df2=None
try: # CLOSE EXISTING BETS
    df2 = pd.read_sql("""
            SELECT Bet.betId As betId, (CASE WHEN isOver THEN T.rank<=Bet.place ELSE T.rank>=Bet.place END) As isWon 
            FROM (SELECT DrivesFor.teamName AS teamName, ROW_NUMBER() OVER(ORDER BY SUM(temp_positions.points) DESC) AS rank
                 FROM temp_positions
                 INNER JOIN Driver
                     ON Driver.name=temp_positions.name
                 INNER JOIN DrivesFor
                     ON Driver.driverId=DrivesFor.driverId
                 GROUP BY DrivesFor.teamName) T
            INNER JOIN Informs
                ON T.teamName=Informs.teamName
            INNER JOIN Bet
                ON Informs.BetId=Bet.BetId
            WHERE Bet.driverId IS NULL
          """, c)
except sqlalchemy.exc.IntegrityError:
    logging.log(logging.INFO, "Repeated keys, double check new race is updated")
except Exception as e:
    logging.log(logging.WARN, f"Internal DB Error: {e}")


c.execute(f"""
          UPDATE Bet
          SET completed=True
          WHERE Bet.raceId={raceId}
          """)
          
