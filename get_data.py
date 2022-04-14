import requests
import pandas as pd 
import xml.etree.ElementTree as ET
import unidecode
import numpy as np
import sqlalchemy
DB_USER = 'pg2682' 
DB_PASSWORD = '7440' 

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
print(df)
    
DB_USER = 'pg2682'  #os.getenv('user')
DB_PASSWORD = '7440'  #os.getenv('password')

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

# This line creates a database engine that knows how to connect to the URI above
engine = sqlalchemy.create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/proj1part2")
c = engine.connect()
df.to_sql('temp_positions', con=c, if_exists='replace')

raceId = next(c.execute("""SELECT raceId
                            FROM Races
                            WHERE raceName=%s
                            AND season=%s""", (race_data['RaceName'], race_data['Date'].split('-')[0])))[0]

print(raceId)
print(list(c.execute("""
          INSERT (driverID, raceID, position, points)
          INTO Competes_Record
          SELECT Driver.driverID, %s, temp_positions.place, temp_positions.points
          FROM temp_positions
          INNER JOIN Driver
            ON Driver.name=temp_positions.name
          """, (raceId,))))

# We need something for existing bets
# FROM HERE, check all informs that reference these races_records and 
# # execute a query for each informs to basically inform them of said information, this ultimately deciding the bet
# By deciding the bet, we can conclude on wager