import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

connection = sqlite3.connect('../../data/bike_logs.db')

query = "SELECT * FROM logs WHERE is_semester = 1 OR is_semester is NULL ORDER BY date ASC"

df = pd.read_sql(query, connection)

# filling missing is_semester and is_weekend values with proper values
# precipitation and bikes_available set to 0 for any null values 
values = {"bikes_available": 0, "docks_available": 0, "is_semester": 1, "is_weekend": 0, "precipitation": 0}
df = df.fillna(value = values)

# converting datatypes
df['bikes_available'] = df['bikes_available'].astype(int)
df['docks_available'] = df['docks_available'].astype(int)
df['date'] = pd.to_datetime(df['date'])
df['is_semester'] = df['is_semester'].astype(int)
df['is_weekend'] = df['is_weekend'].astype(int)
df['day_of_week'] = df['date'].dt.day_name()

# transforming data
# use time to find 5 min after class ends
    #

mwf_times =[['08:50:00', '08:55:00'],
            ['09:55:00', '10:00:00'],
            ['11:00:00', '11:05:00'],
            ['12:05:00', '12:10:00'],
            ['13:10:00', '13:15:00'],
            ['14:15:00', '14:20:00'],
            ['15:20:00', '15:25:00'],
            ['16:25:00', '16:30:00'],
            ['17:30:00', '17:35:00'],
            ['18:35:00', '18:40:00']]

mwf_times = np.array(mwf_times, dtype=object)

tt_times = [['09:15:00', '09:20:00'],
            ['10:45:00', '10:50:00'],
            ['12:15:00', '12:20:00'],
            ['13:45:00', '13:50:00'],
            ['15:15:00', '15:20:00'],
            ['16:45:00', '16:50:00'],
            ['18:15:00', '18:20:00']]

weekdays = np.array(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], dtype=object)

    
def isRelease(a, b):
    if [(a == weekdays[0]) | (a == weekdays[2]) | (a == weekdays[4])]:
        for i in range(0,9):
            if [(b >= mwf_times[i][0]) & (b <= mwf_times[i][1])]:
                return 'true'
            else:
                return 'false'
    else:
        return 'false'
        
df['release_period'] = isRelease(df['day_of_week'], df['time'])

print(df.head(10))