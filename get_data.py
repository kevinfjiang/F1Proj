import requests
import sqlalchemy 
import pandas as pd 
DB_USER = 'pg2682' 
DB_PASSWORD = '7440' 

DB_SERVER = 'w411.cisxo9blonu.us-east-1.rds.amazonaws.com' 

url = "http://ergast.com/api/f1/2022/drivers" 



payload={}
headers = {}
response = requests.request("GET", url, headers=headers, data=payload)

df = pd.read_xml(response.text)

print(df)
