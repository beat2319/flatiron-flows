import sqlite3
import pandas as pd
import numpy as np
import datetime as dt
import time
import timeit
import pytz

conn = sqlite3.connect('../data/bikeLogs_backup.db')

query = "SELECT * FROM bike_logs"

df_webhook = pd.DataFrame({
    'station_id':pd.Series([], dtype = 'object'), 
    'num_bikes_available':pd.Series([], dtype = 'object'),  
    'temp':pd.Series([], dtype = 'object'),  
    'wind_speed':pd.Series([], dtype = 'object'),  
    'campus_rain':pd.Series([], dtype = 'object'),
    'precipitation': pd.Series([], dtype = 'object'),
    'dttime':pd.Series([], dtype = 'object'),
})

df_webhook = pd.read_sql(query, conn)

# converting datatypes
df_webhook['num_bikes_available'] = df_webhook['num_bikes_available'].astype(int)
df_webhook['dttime'] = pd.to_datetime(df_webhook.dttime, format='%y%m%d%H%M%S')

def calculate_pickups(df):
    #start = time.time()

    df['curr'] = df['num_bikes_available']

    #index = pickups_df['station_id'].nunique()
    #pickups_df['prev'] = pickups_df['bikes_available'].shift(periods = index, fill_value = 0)
    df['prev'] = df.groupby('station_id')['num_bikes_available'].shift(fill_value = 0)

    df['difference'] = df['prev'] - df['curr']
    df[['difference']].infer_objects().fillna(0)
    df['difference'].astype(int)

    conditions = [
        (df['difference'] <= 0),
        (df['difference'] > 0)
    ]
    choices = [
        0, 
        df['difference']
    ]
    df.drop(columns=['curr'],inplace = True)
    df.drop(columns=['prev'],inplace = True)
    df.drop(columns=['difference'],inplace = True)

    df['pickups'] = np.select(conditions, choices)
    df.drop(columns=['num_bikes_available'],inplace = True)

    # end = time.time()
    # print("pickups:", end - start)
    return df['pickups']

def webhooks(df):
    df['pickups'] = calculate_pickups(df)
    pickups_total = df.groupby('station_id').resample('d', on='dttime')['pickups'].count()
    campus_rain_mean = df.resample('d', on='dttime')['campus_rain'].mean()
    boulder_rain_mean = df.resample('d', on='dttime')['precipitation'].mean()
    temp_mean = df.resample('d', on='dttime')['temp'].mean()
    wind_mean = df.resample('d', on='dttime')['wind_speed'].mean()

    return temp_mean

if __name__ == '__main__':
    print(webhooks(df_webhook))