import requests
import sqlite3
import pandas as pd
import numpy as np
import datetime as dt
import pytz
import json
import os
from json import loads, dumps
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns
import shutil

load_dotenv('.env')
webhook_url = os.getenv('BIKELOGS_WEBHOOK')

conn = sqlite3.connect('./data/bike_logs.db')

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

# print(df_webhook['hours'])
now = dt.datetime.now(local_timezone)
current_time = now.strftime('%Y-%m-%d')
df_filtered = df_webhook[df_webhook['dttime'].dt.strftime('%Y-%m-%d') == current_time]


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
    # df.drop(columns=['curr'],inplace = True)
    # df.drop(columns=['prev'],inplace = True)
    # df.drop(columns=['difference'],inplace = True)

    df['pickups'] = np.select(conditions, choices)
    # df.drop(columns=['num_bikes_available'],inplace = True)

    # end = time.time()
    # print("pickups:", end - start)
    return df['pickups']

# may want to shift by 5 as value changes every 5 min
# also should make sure that it resets every day, just by only returning 0 if value is negative 
# otherwise good i think
def calculate_campus_rain(df):
    df['curr'] = df['campus_rain']
    df['prev'] = df.groupby('station_id')['campus_rain'].shift(periods=5, fill_value = 0)
    df['difference'] = df['curr'] - df['prev']

    df['campus_rain'] = df['difference']

    # df.drop(columns=['curr'],inplace = True)
    # df.drop(columns=['prev'],inplace = True)
    # df.drop(columns=['difference'],inplace = True)

    return df['campus_rain']

def pickups_graph(df, current_time):
    df['pickups'] = calculate_pickups(df)
    pickups_total = df.groupby('station_id', as_index=False)['pickups'].sum()
    pickups_total['station_id'] = pickups_total['station_id'].str.replace('bcycle_boulder_', ' ')
    pickups_graph = sns.barplot(data=pickups_total, x="station_id", y ="pickups", palette="Set2")
    pickups_graph.set_title(f'Total Pickups by Station ({current_time})')
    pickups_graph.set_ylabel('Total Pickups')
    pickups_graph.set_xlabel('Station')
    # plt.savefig("../../hosting/graph/images/pickups_graph.png")
    plt.savefig("./images/pickups_graph.png")

def campus_rain_graph(df, current_time):
    df['campus_rain'] = calculate_campus_rain(df)
    campus_rain_mean = df.groupby('hours', as_index=False)['campus_rain'].mean()
    campus_rain_graph = sns.relplot(data = campus_rain_mean, x= 'hours', y='campus_rain', kind='line')
    campus_rain_graph.figure.subplots_adjust(top=0.9)
    campus_rain_graph.figure.suptitle(f'Campus Rain by Hour ({current_time})')
    campus_rain_graph.set_ylabels('Campus Rain in Inches')
    campus_rain_graph.set_xlabels('Hours')
    # plt.savefig("../../hosting/graph/images/campus_rain_graph.png")
    plt.savefig("./images/campus_rain_graph.png")

def temp_graph(df, current_time):
    temp_mean = df.groupby('hours', as_index=False)['temp'].mean()
    temp_graph = sns.relplot(data = temp_mean, x= 'hours', y='temp', kind='line')
    temp_graph.figure.subplots_adjust(top=0.9)
    temp_graph.figure.suptitle(f'Temperature by Hour ({current_time})')
    temp_graph.set_ylabels('Temperature in °F')
    temp_graph.set_xlabels('Hours')
    # plt.savefig("../../hosting/graph/images/temp_graph.png")
    plt.savefig("./images/temp_graph.png")

def boulder_rain_graph(df, current_time):
    boulder_rain_mean = df.groupby('hours', as_index=False)['precipitation'].mean()
    boulder_rain_graph = sns.relplot(data = boulder_rain_mean, x= 'hours', y='precipitation', kind='line')
    boulder_rain_graph.figure.subplots_adjust(top=0.9)
    boulder_rain_graph.figure.suptitle(f'Boulder Precipitation by Hour ({current_time})')
    boulder_rain_graph.set_ylabels('Boulder Precipitation in Inches')
    boulder_rain_graph.set_xlabels('Hours')
    # plt.savefig("../../hosting/graph/images/boulder_rain_graph.png")
    plt.savefig("./images/boulder_rain_graph.png")

def wind_graph(df, current_time):
    wind_mean = df.groupby('hours', as_index=False)['wind_speed'].mean()
    wind_graph = sns.relplot(data = wind_mean, x= 'hours', y='wind_speed', kind='line')
    wind_graph.figure.subplots_adjust(top=0.9)
    wind_graph.figure.suptitle(f'Wind Speed by Hour ({current_time})')
    wind_graph.set_ylabels('Wind in MPH')
    wind_graph.set_xlabels('Hours')
    # plt.savefig("../../hosting/graph/images/wind_graph.png")
    plt.savefig("./images/wind_graph.png")

def webhooks(df, time):

    # d='2025-09-09 22:44:09' 
    # date=pd.to_datetime(d)
    # current_time = date.strftime('%Y-%m-%d')
    df['hours'] = pd.to_datetime(df['dttime']).dt.hour

    # campus_rain_mean = df_filtered['campus_rain'].mean()

    pickups_graph(df, time)
    campus_rain_graph(df, time)
    temp_graph(df, time)
    boulder_rain_graph(df, time)
    wind_graph(df, time)

    # plt.show()
    # payload = {
    #     file: "./pickups_graph.png",
    # }


    campus_rain = {
        "description": "average of campus rain by hour",
        # "payload" : pickups_graph.png,
        "title": "Campus Rain",
        "color": 1127128,
        "image": {
            "url": "attachment://campus_rain_graph.png"
        }
    }

    boulder_rain = {
        "description": "average of boulder precipitation by hour",
        # "payload" : pickups_graph.png,
        "title": "Boulder Precipitation",
        "color": 1127128,
        "image": {
            "url": "attachment://boulder_rain_graph.png"
        }
    }

    pickups = {
        "description": "sum of pickups by station",
        "title": "Total Pickups",
        "color": 14177041,
        "image": {
            "url": "attachment://pickups_graph.png"
        }
    }

    temp = {
        "description": "average of temperature by hour",
        # "payload" : pickups_graph.png,
        "title": "Temperature",
        "color": 16776960,
        "image": {
            "url": "attachment://temp_graph.png"
        }
    }

    wind_speed = {
        "description": "average of wind speed by hour",
        # "payload" : pickups_graph.png,
        "title": "Wind Speed",
        "color": 16777215,
        "image": {
            "url": "attachment://wind_graph.png"
        }
    }

    # will add this later will upload a new pick of dog daily
    # basicall
    # chat = {
    #     "description": "hope you had a goated day",
    #     # "payload" : pickups_graph.png,
    #     "title": "Hello Josephone",
    #     "color": 1127128,
    #     "image": {
    #         "url": "attachment://wind_graph.png"
    #     }
    # }

    

    payload = {
        "content": f"Data Backed Up ({current_time})",
        "username": "Daily Updates",
        "embeds": [
            pickups,
            campus_rain,
            boulder_rain,
            temp,
            wind_speed
            ],
    }

    data = {
        'payload_json': (None, json.dumps(payload), 'application/json'),
        'file1': ('pickups_graph.png', open('./images/pickups_graph.png', 'rb'), 'image/png'),
        'file2': ('campus_rain_graph.png', open('./images/campus_rain_graph.png', 'rb'), 'image/png'),
        'file3': ('boulder_rain_graph.png', open('./images/boulder_rain_graph.png', 'rb'), 'image/png'),
        'file4': ('temp_graph.png', open('./images/temp_graph.png', 'rb'), 'image/png'),
        'file5': ('wind_graph.png', open('./images/wind_graph.png', 'rb'), 'image/png')

    }
    

    result = requests.post(webhook_url, files=data)
    if 200 <= result.status_code < 300:
        print(f"Webhook sent {result.status_code}")
    else:
        print(f"Not sent with {result.status_code}, response:\n{result.json()}")

def backup_data():
    src = './data/bike_logs.db'
    dst = './data/bikeLogs_backup.db'

    shutil.copy(src, dst)

if __name__ == '__main__':
    webhooks(df_filtered, current_time)
    backup_data()