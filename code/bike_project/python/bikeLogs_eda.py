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

# 2D and 1D arrays to organize specific times and days
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

weekdays = np.array(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], dtype=object)

# using numpy.select to statically "loop" through the day_of_week and time dataframes 
# columns and compare with mwf_time, tt_time, and weekdays respecively
conditions = [
    (((df['day_of_week'] == weekdays[0]) | 
      (df['day_of_week'] == weekdays[2]) | 
      (df['day_of_week'] == weekdays[4])) & 
       (((df['time'] >= mwf_time[0][0]) & (df['time'] <= mwf_time[0][1])) | 
        ((df['time'] >= mwf_time[1][0]) & (df['time'] <= mwf_time[1][1])) | 
        ((df['time'] >= mwf_time[2][0]) & (df['time'] <= mwf_time[2][1])) |
        ((df['time'] >= mwf_time[3][0]) & (df['time'] <= mwf_time[3][1])) |
        ((df['time'] >= mwf_time[4][0]) & (df['time'] <= mwf_time[4][1])) |
        ((df['time'] >= mwf_time[5][0]) & (df['time'] <= mwf_time[5][1])) |
        ((df['time'] >= mwf_time[6][0]) & (df['time'] <= mwf_time[6][1])) |
        ((df['time'] >= mwf_time[7][0]) & (df['time'] <= mwf_time[7][1])) |
        ((df['time'] >= mwf_time[8][0]) & (df['time'] <= mwf_time[8][1])) |
        ((df['time'] >= mwf_time[9][0]) & (df['time'] <= mwf_time[9][1])))) |
    (((df['day_of_week'] == weekdays[1]) | 
      (df['day_of_week'] == weekdays[3])) & 
       (((df['time'] >= tt_time[0][0]) & (df['time'] <= tt_time[0][1])) | 
        ((df['time'] >= tt_time[1][0]) & (df['time'] <= tt_time[1][1])) | 
        ((df['time'] >= tt_time[2][0]) & (df['time'] <= tt_time[2][1])) |
        ((df['time'] >= tt_time[3][0]) & (df['time'] <= tt_time[3][1])) |
        ((df['time'] >= tt_time[4][0]) & (df['time'] <= tt_time[4][1])) |
        ((df['time'] >= tt_time[5][0]) & (df['time'] <= tt_time[5][1])) |
        ((df['time'] >= tt_time[6][0]) & (df['time'] <= tt_time[6][1])))),
]
choices = [
    True
]

df['release_period'] = np.select(conditions, choices, default=False)

# using pandas apply and lambda to apply specific function to the dataframe         
# df['release_period'] = df.apply(lambda x: isRelease(x['day_of_week'], x['time']), axis=1)

print(list(df))
#print(df.query('release_period == True').head(50))
print(df.query('release_period == True').tail(50))
#print(df)