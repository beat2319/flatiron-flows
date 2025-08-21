#!/usr/src/app/opt/conda/bin/python
import requests
import numpy as np
import pandas as pd
import datetime as dt
import time
import sqlite3
import lxml
import logging as logger
import os
from dotenv import load_dotenv

#boulder_weather = https://api.weather.gov/gridpoints/BOU/54,74/forecast/hourly
precip_url = "https://api.open-meteo.com/v1/forecast?latitude=40.0073&longitude=-105.2660&current=precipitation"
weather_url = "https://sundowner.colorado.edu/weather/atoc1/"
bcycle_url = "https://gbfs.bcycle.com/bcycle_boulder/"

#setting up discord webhook
load_dotenv('.env')
webhook_url = os.getenv('BIKELOGS_WEBHOOK')

# set as object to trick pandas to preserve datatype
log_df = pd.DataFrame({
    'station_id':pd.Series([], dtype = 'object'), 
    # 'name':pd.Series([], dtype = 'object'), 
    # 'lon':pd.Series([], dtype = 'object'), 
    # 'lat':pd.Series([], dtype = 'object'),  
    # 'num_docks_available':pd.Series([], dtype = 'object'),  
    'num_bikes_available':pd.Series([], dtype = 'object'),  
    'temp':pd.Series([], dtype = 'object'),  
    'wind_speed':pd.Series([], dtype = 'object'),  
    'campus_rain':pd.Series([], dtype = 'object'),
    'precipitation': pd.Series([], dtype = 'object'),
    'dttime':pd.Series([], dtype = 'object'),
})

station_array = np.array([0, 14, 19, 29, 34, 35, 37, 40, 42, 44, 47, 52, 53])

request_names = ['station_information', 'station_status']

# gets the bycle json based on the request name
# and verifies the respose code status
def get_bcycle_json(name):
    url = f"{bcycle_url}{name}"
    response = requests.get(url)

    if response.status_code == 200:
        bcycle_data = response.json()
        return bcycle_data
    else:
        print(f"Failed to retrive data {response.status_code}")
        logger.error(response.status_code)

# this function parse the station info json 
# only returns the chosen info columns as df
def parse_info(df):
    bcycle_json = get_bcycle_json(request_names[0])
    if bcycle_json:
        for i in range(len(station_array)):
            if 'station_id' == df.columns[0]:
                df.at[i, df.columns[0]] = bcycle_json["data"]["stations"][station_array[i]]['station_id']

# this function parse the station status json 
# only returns the chosen status columns as df
def parse_status(df):
    bcycle_json = get_bcycle_json(request_names[1])
    if bcycle_json:
        for i in range(len(station_array)):
            if 'num_bikes_available' == df.columns[1]:
                df.at[i, df.columns[1]] = bcycle_json["data"]["stations"][station_array[i]]['num_bikes_available']
            # if status_columns[1] == df.columns[2]:
            #     df.at[i, df.columns[2]] = bcycle_json["data"]["stations"][station_array[i]][status_columns[1]]

# parses throught the scraped table as a dataframe
# and verifies the respose code status
def get_weather_table(index):
    url = weather_url
    response = requests.get(url)

    if response.status_code == 200:
        content = response.content
        df = pd.read_html(content)[index]
        return df
    else:
        print(f"Failed to retrive data {response.status_code}")
        logger.error(response.status_code)

weather_array = np.array([[0,5,8],
                         ['temp', 'wind_speed', 'campus_rain']], dtype = object)

# this function takes in the weather table as dataframe
# adds the parsed temp, wind and rain to the dataframe
def parse_weather(df):
    scrape_df = get_weather_table(0)
    if not scrape_df.empty:
        columns = scrape_df.columns[1]
        for i in range(len(station_array)):
            if weather_array[1][0] == df.columns[2]:
                df.at[i, df.columns[2]] = scrape_df[columns][weather_array[0][0]]
            if weather_array[1][1] == df.columns[3]:
                df.at[i, df.columns[3]] = scrape_df[columns][weather_array[0][1]]
            if weather_array[1][2] == df.columns[4]:
                df.at[i, df.columns[4]] = scrape_df[columns][weather_array[0][2]]

def get_precip_json():
    url = f"{precip_url}"
    response = requests.get(url)

    if response.status_code == 200:
        precip_data = response.json()
        return precip_data
    else:
        print(f"Failed to retrive data {response.status_code}")
        logger.debugf("Failed to retrive data {statusCode}", statusCode=response.status_code)

def parse_precip(df):
    precip_json = get_precip_json()
    if precip_json:
        for i in range(len(station_array)):
            df.at[i, df.columns[5]] = precip_json["current"]["precipitation"]

# this function gets the current datetime 
# and adds date and time to the dataframe
def parse_datetime(df):
    now = dt.datetime.now()
    for i in range(len(station_array)):
        df.at[i, df.columns[6]] = now.strftime('%y%m%d%H%M%S')

def log_data(df):
    parse_weather(df)
    parse_info(df)
    parse_status(df)
    parse_datetime(df)
    parse_precip(df)
    conn = sqlite3.connect('/usr/src/app/data/bike_logs.db')
    df.to_sql(name='bike_logs', con=conn, if_exists='append', index=False)

    data = {
    "content": "data logged",
    "username": "dataLogger_user",
    }
    result = requests.post(webhook_url, json=data)
    if 200 <= result.status_code < 300:
        print(f"Webhook sent {result.status_code}")
    else:
        print(f"Not sent with {result.status_code}, response:\n{result.json()}")



if __name__ == '__main__':
    
    log_data(log_df)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    #print(df.dtypes)
    # parse_json()
    # print(df.head(5))