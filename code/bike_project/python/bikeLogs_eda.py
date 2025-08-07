import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import time

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

def calculate_release():
    release_df = pd.DataFrame({
        'station_id':pd.Series([], dtype = 'object'),
        'date':pd.Series([], dtype = 'object'), 
        'time':pd.Series([], dtype = 'object'), 
        'day_of_week':pd.Series([], dtype = 'object'), 
        'output':pd.Series([], dtype = 'object'), 
    })

    release_df['station_id'] = df['station_id']
    release_df['date'] = df['date']
    release_df['time'] = df['time']
    release_df['day_of_week'] = release_df['date'].dt.day_name()

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

    conditions = [
        (((release_df['day_of_week'] == weekdays[0]) | 
        (release_df['day_of_week'] == weekdays[2]) | 
        (release_df['day_of_week'] == weekdays[4])) & 
        (((release_df['time'] >= mwf_time[0][0]) & (release_df['time'] <= mwf_time[0][1])) | 
            ((release_df['time'] >= mwf_time[1][0]) & (release_df['time'] <= mwf_time[1][1])) | 
            ((release_df['time'] >= mwf_time[2][0]) & (release_df['time'] <= mwf_time[2][1])) |
            ((release_df['time'] >= mwf_time[3][0]) & (release_df['time'] <= mwf_time[3][1])) |
            ((release_df['time'] >= mwf_time[4][0]) & (release_df['time'] <= mwf_time[4][1])) |
            ((release_df['time'] >= mwf_time[5][0]) & (release_df['time'] <= mwf_time[5][1])) |
            ((release_df['time'] >= mwf_time[6][0]) & (release_df['time'] <= mwf_time[6][1])) |
            ((release_df['time'] >= mwf_time[7][0]) & (release_df['time'] <= mwf_time[7][1])) |
            ((release_df['time'] >= mwf_time[8][0]) & (release_df['time'] <= mwf_time[8][1])) |
            ((release_df['time'] >= mwf_time[9][0]) & (release_df['time'] <= mwf_time[9][1])))) |
        (((release_df['day_of_week'] == weekdays[1]) | 
        (release_df['day_of_week'] == weekdays[3])) & 
        (((release_df['time'] >= tt_time[0][0]) & (release_df['time'] <= tt_time[0][1])) | 
            ((release_df['time'] >= tt_time[1][0]) & (release_df['time'] <= tt_time[1][1])) | 
            ((release_df['time'] >= tt_time[2][0]) & (release_df['time'] <= tt_time[2][1])) |
            ((release_df['time'] >= tt_time[3][0]) & (release_df['time'] <= tt_time[3][1])) |
            ((release_df['time'] >= tt_time[4][0]) & (release_df['time'] <= tt_time[4][1])) |
            ((release_df['time'] >= tt_time[5][0]) & (release_df['time'] <= tt_time[5][1])) |
            ((release_df['time'] >= tt_time[6][0]) & (release_df['time'] <= tt_time[6][1])))),
    ]
    choices = [
        True
    ]
    release_df['output'] = np.select(conditions, choices, default=False)
    # end = time.time()
    # print("release:", end - start)
    return release_df

def calculate_pickups():
    #start = time.time()
    pickups_df = pd.DataFrame({
        'station_id':pd.Series([], dtype = 'object'),
        'bikes_available':pd.Series([], dtype = 'object'), 
        'prev':pd.Series([], dtype = 'object'), 
        'curr':pd.Series([], dtype = 'object'), 
        'output':pd.Series([], dtype = 'object'), 
    })

    
    pickups_df['station_id'] = df['station_id']
    pickups_df['bikes_available'] = df['bikes_available']
    pickups_df['curr'] = pickups_df['bikes_available']

    index = pickups_df['station_id'].nunique()
    pickups_df['prev'] = pickups_df['bikes_available'].shift(periods = index, fill_value = 0)

    pickups_df['output'] = pickups_df['prev'] - pickups_df['curr']
    pickups_df['output'] = pickups_df[['output']].infer_objects().fillna(0)
    pickups_df['output'] = pickups_df['output'].astype(int)

    conditions = [
        (pickups_df['output'] <= 0),
        (pickups_df['output'] > 0)
    ]
    choices = [
        0, 
        pickups_df['output']
    ]
    pickups_df['output'] = np.select(conditions, choices)

    # end = time.time()
    # print("pickups:", end - start)
    return pickups_df


if __name__ == '__main__':
    # print(df_bikes.head(20))
    test_one = calculate_pickups()
    print(test_one.head(10))
    test_two = calculate_release()
    print(test_two.head(10))