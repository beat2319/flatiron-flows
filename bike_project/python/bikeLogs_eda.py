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

# 2d and 1d arrays to organize specific times and days
mwf_time =np.array([['08:50:00', '08:55:00'],
                    ['09:55:00', '10:00:00'],
                    ['11:00:00', '11:05:00'],
                    ['12:05:00', '12:10:00'],
                    ['13:10:00', '13:15:00'],
                    ['14:15:00', '14:20:00'],
                    ['15:20:00', '15:25:00'],
                    ['16:25:00', '16:30:00'],
                    ['17:30:00', '17:35:00'],
                    ['18:35:00', '18:40:00']],  dtype=object)


tt_time = np.array([['09:15:00', '09:20:00'],
                    ['10:45:00', '10:50:00'],
                    ['12:15:00', '12:20:00'],
                    ['13:45:00', '13:50:00'],
                    ['15:15:00', '15:20:00'],
                    ['16:45:00', '16:50:00'],
                    ['18:15:00', '18:20:00']], dtype=object)

mwf_days = np.array(['Monday', 'Wednesday', 'Friday'], dtype=object)

tt_days = np.array(['Tuesday', 'Thursday'], dtype=object)

# function that takes in the dataframe columns time and day 
# of week then loops through arrays to see if the columns 
# have the given array values 

def isRelease(x,y):
    for i in range(0,len(mwf_days)):
        if x == mwf_days[i]:
            for j in range(0,len(mwf_time)):
                if y >= mwf_time[j][0] and y <= mwf_time[j][1]:
                    return True
    for i in range(0,len(tt_days)):
        if x == tt_days[i]:
            for j in range(0,len(tt_time)):
                if y >= tt_time[j][0] and y <= tt_time[j][1]:
                    return True
    else:
        return False

# using pandas apply and lambda to apply specific function to the dataframe         
df['release_period'] = df.apply(lambda x: isRelease(x['day_of_week'], x['time']), axis=1)

print(df.query('release_period == True').head(50))
