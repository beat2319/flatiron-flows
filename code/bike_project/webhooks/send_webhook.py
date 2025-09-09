import requests
import sqlite3
import pandas as pd
import numpy as np
import datetime as dt
import time
import timeit
import pytz
import os
from json import loads, dumps
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns

load_dotenv('.env')
webhook_url = os.getenv('BIKELOGS_WEBHOOK')

conn = sqlite3.connect('../data/bike_logs.db')

query = "SELECT * FROM bike_logs"

df_webhook = pd.DataFrame({
    'station_id':pd.Series([], dtype = 'object'), 
    'num_bikes_available':pd.Series([], dtype = 'object'),  
    'temp':pd.Series([], dtype = 'object'),  
    'wind_speed':pd.Series([], dtype = 'object'),  
    'campus_rain':pd.Series([], dtype = 'object'),
    'precipitation': pd.Series([], dtype = 'object'),
    'dttime':pd.Series([], dtype = 'object'),
    'hours':pd.Series([], dtype = 'object'),
})

df_webhook = pd.read_sql(query, conn)

# converting datatypes
local_timezone = pytz.timezone('America/Denver')
df_webhook['num_bikes_available'] = df_webhook['num_bikes_available'].astype(int)
df_webhook['dttime'] = pd.to_datetime(df_webhook.dttime)
df_webhook['dttime'] = pd.to_datetime(df_webhook['dttime'].dt.tz_localize('UTC').dt.tz_convert(local_timezone))
df_webhook['hours'] = pd.to_datetime(df_webhook['dttime'].dt.strftime('%H'))

print(df_webhook['hours'])

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

# may want to shift by 5 as value changes every 5 min
# also should make sure that it resets every day, just by only returning 0 if value is negative 
# otherwise good i think
def calculate_campus_rain(df):
    df['curr'] = df['campus_rain']
    df['prev'] = df.groupby('station_id')['campus_rain'].shift(periods=5, fill_value = 0)
    df['difference'] = df['prev'] - df['curr']

    df['campus_rain'] = df['difference']

    df.drop(columns=['curr'],inplace = True)
    df.drop(columns=['prev'],inplace = True)
    df.drop(columns=['difference'],inplace = True)

    return df['campus_rain']

def webhooks(df):
    df['pickups'] = calculate_pickups(df)
    df['campus_rain'] = calculate_campus_rain(df)
    # df['pickups'] = 'pickups_' + df['pickups'].astype(str)

    # now = pd.to_datetime('2025-08-26', format='%Y-%m-%d')
    now = dt.datetime.now(local_timezone)
    current_time = now.strftime('%Y-%m-%d')

    # main_query = f'dttime == {now}'
    df_filtered = df[df['dttime'].dt.strftime('%Y-%m-%d') == current_time]
    pickups_total = df_filtered.groupby('station_id', as_index=False)['pickups'].sum()
    #campus_rain_mean = df_filtered.groupby('hour', as_index=False)['campus_rain'].mean()
    # campus_rain_mean = df_filtered['campus_rain'].mean()
    boulder_rain_mean = df_filtered['precipitation'].mean()
    temp_mean = df_filtered['temp'].mean()
    wind_mean = df_filtered['wind_speed'].mean()
    # campus_rain_mean = df.resample('d', on='dttime')['campus_rain'].mean()
    # boulder_rain_mean = df.resample('d', on='dttime')['precipitation'].mean()
    # temp_mean = df.resample('d', on='dttime')['temp'].mean()
    # wind_mean = df.resample('d', on='dttime')['wind_speed'].mean()
    pickups_total['station_id'] = pickups_total['station_id'].str.replace('bcycle_boulder_', '')
    #print(campus_rain_mean)
    ax = sns.barplot(data=pickups_total, x="station_id", y ="pickups", palette="Set2")
    ax.set_title(f'Total Pickups by Station ({current_time})')
    ax.set_ylabel('Total Pickups')
    ax.set_xlabel('Station')
    # pickups_total.plot(kind = 'bar' )
    plt.show()

    weather = {
        "description": "text in embed",
        "title": "embed title",
        "color": 1127128
        }
    
    total = {
        "description": str(),
        "title": "embed title",
        "color": 14177041
    }
    

    data = {
        "content": "Data Backed Up",
        "username": "Daily Updates",
        "embeds": [
            weather,
            total
            ],
    }

    # result = requests.post(webhook_url, json=data)
    # if 200 <= result.status_code < 300:
    #     print(f"Webhook sent {result.status_code}")
    # else:
    #     print(f"Not sent with {result.status_code}, response:\n{result.json()}")


if __name__ == '__main__':
    webhooks(df_webhook)