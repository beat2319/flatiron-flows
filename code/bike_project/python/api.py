import requests
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import time
import sqlite3

#boulder_weather = https://api.weather.gov/gridpoints/BOU/54,74/forecast/hourly
precip_url = "https://api.open-meteo.com/v1/forecast?latitude=40.0073&longitude=-105.2660&current=precipitation"
weather_url = "https://sundowner.colorado.edu/weather/atoc1/"
bcycle_url = "https://gbfs.bcycle.com/bcycle_boulder/"

# set as object to trick pandas to preserve datatype
df = pd.DataFrame({
    'station_id':pd.Series([], dtype = 'object'), 
    'name':pd.Series([], dtype = 'object'), 
    'lon':pd.Series([], dtype = 'object'), 
    'lat':pd.Series([], dtype = 'object'),  
    'num_docks_available':pd.Series([], dtype = 'object'),  
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

info_columns = ['station_id', 'name', 'lon', 'lat']

# this function parse the station info json 
# only returns the chosen info columns as df
def parse_info():
    bcycle_json = get_bcycle_json(request_names[0])
    if bcycle_json:
        for i in range(len(station_array)):
            if info_columns[0] == df.columns[0]:
                df.at[i, df.columns[0]] = bcycle_json["data"]["stations"][station_array[i]][info_columns[0]]
            if info_columns[1] == df.columns[1]:
                df.at[i, df.columns[1]] = bcycle_json["data"]["stations"][station_array[i]][info_columns[1]]
            if info_columns[2] == df.columns[2]:
                df.at[i, df.columns[2]] = bcycle_json["data"]["stations"][station_array[i]][info_columns[2]]
            if info_columns[3] == df.columns[3]:
                df.at[i, df.columns[3]] = bcycle_json["data"]["stations"][station_array[i]][info_columns[3]]

status_columns = ['num_docks_available', 'num_bikes_available']

# this function parse the station status json 
# only returns the chosen status columns as df
def parse_status():
    bcycle_json = get_bcycle_json(request_names[1])
    if bcycle_json:
        for i in range(len(station_array)):
            if status_columns[0] == df.columns[4]:
                df.at[i, df.columns[4]] = bcycle_json["data"]["stations"][station_array[i]][status_columns[0]]
            if status_columns[1] == df.columns[5]:
                df.at[i, df.columns[5]] = bcycle_json["data"]["stations"][station_array[i]][status_columns[1]]

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

weather_array = np.array([[0,5,8],
                         ['temp', 'wind_speed', 'campus_rain']], dtype = object)

# this function takes in the weather table as dataframe
# adds the parsed temp, wind and rain to the dataframe
def parse_weather():
    scrape_df = get_weather_table(0)
    if not scrape_df.empty:
        columns = scrape_df.columns[1]
        for i in range(len(station_array)):
            if weather_array[1][0] == df.columns[6]:
                df.at[i, df.columns[6]] = scrape_df[columns][weather_array[0][0]]
            if weather_array[1][1] == df.columns[7]:
                df.at[i, df.columns[7]] = scrape_df[columns][weather_array[0][1]]
            if weather_array[1][2] == df.columns[8]:
                df.at[i, df.columns[8]] = scrape_df[columns][weather_array[0][2]]

def get_precip_json():
    url = f"{precip_url}"
    response = requests.get(url)

    if response.status_code == 200:
        precip_data = response.json()
        return precip_data
    else:
        print(f"Failed to retrive data {response.status_code}")

def parse_precip():
    precip_json = get_precip_json()
    if precip_json:
        for i in range(len(station_array)):
            df.at[i, df.columns[9]] = precip_json["current"]["precipitation"]

# this function gets the current datetime 
# and adds date and time to the dataframe
def parse_datetime():
    now = dt.datetime.now()
    for i in range(len(station_array)):
        df.at[i, df.columns[10]] = now.strftime('%y%m%d%H%M%S')




if __name__ == '__main__':
    start = time.time()

    parse_weather()
    parse_info()
    parse_status()
    parse_datetime()
    parse_precip()

    end = time.time()
    print(end - start)
    
    print(df)
    conn = sqlite3.connect('new_bike_logs.db')
    c = conn.cursor()
    df.to_sql(name='bike_logs', con=conn, if_exists='append', index=False)
    #print(df.dtypes)
    # parse_json()
    # print(df.head(5))