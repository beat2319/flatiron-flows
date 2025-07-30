import requests
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd

#boulder_weather = https://api.weather.gov/gridpoints/BOU/54,74/forecast/hourly
station_url = "https://sundowner.colorado.edu/weather/atoc1/"
bcycle_url = "https://gbfs.bcycle.com/bcycle_boulder/"

df = pd.DataFrame({
    'station_id':pd.Series([], dtype = 'str'), 
    'name':pd.Series([], dtype = 'str'), 
    'lon':pd.Series([], dtype = 'float'), 
    'lat':pd.Series([], dtype = 'float'),  
    'num_docks_available':pd.Series([], dtype = 'int'),  
    'num_bikes_available':pd.Series([], dtype = 'int'),  
    'temp':pd.Series([], dtype = 'float'),  
    'wind_speed':pd.Series([], dtype = 'float'),  
    'total_rain':pd.Series([], dtype = 'float'),  
})

station_array = np.array([0, 14, 19, 29, 34, 35, 37, 40, 42, 44, 47, 52, 53])

request_names = [
    'station_information',
    'station_status'
]

def get_bcycle_json(name):
    url = f"{bcycle_url}{name}"
    response = requests.get(url)

    if response.status_code == 200:
        bcycle_data = response.json()
        return bcycle_data
    else:
        print(f"Failed to retrive data {response.status_code}")

def parse_json():
    for i in range(len(request_names)):
        bcycle_json = get_bcycle_json(request_names[i])
        if bcycle_json:
            for j in range(len(station_array)):
                if i == 0:
                    for k in range(len(info_columns)):
                        df = pd.DataFrame({info_columns[k]: [bcycle_json["data"]["stations"][station_array[j]][info_columns[k]]]})
                        print(df)
                        print(station_array[j], "==", bcycle_json["data"]["stations"][station_array[j]][info_columns[k]])
                if i == 1:
                    for k in range(len(status_columns)):
                        df = pd.DataFrame({status_columns[k]: [bcycle_json["data"]["stations"][station_array[j]][status_columns[k]]]})
                        print(df)
                        print(station_array[j], "==", bcycle_json["data"]["stations"][station_array[j]][status_columns[k]])

info_columns = ['station_id', 'name', 'lon', 'lat']

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

def parse_status():
    bcycle_json = get_bcycle_json(request_names[1])
    if bcycle_json:
        for i in range(len(station_array)):
            if status_columns[0] == df.columns[4]:
                df.at[i, df.columns[4]] = bcycle_json["data"]["stations"][station_array[i]][status_columns[0]]
            if status_columns[1] == df.columns[5]:
                df.at[i, df.columns[5]] = bcycle_json["data"]["stations"][station_array[i]][status_columns[1]]

# parses throught the scraped table as a dataframe
def get_weather_table(index):
    url = station_url
    response = requests.get(url)

    if response.status_code == 200:
        content = response.content
        df = pd.read_html(content)[index]
        return df
    else:
        print(f"Failed to retrive data {response.status_code}")

weather_array = np.array([[0,5,8],
                         ['temp', 'wind_speed', 'total_rain']], dtype = object)

# this function takes in the weather table as dataframe
# adds the parsed temp, wind and rain to the dataframe
def parse_weather():
    scrape_df = get_weather_table(0)
    if not scrape_df.empty:
        df_columns = scrape_df.columns[1]
        for i in range(len(station_array)):
            if weather_array[1][0] == df.columns[6]:
                df.at[i, df.columns[6]] = scrape_df[df_columns][weather_array[0][0]]
            if weather_array[1][1] == df.columns[7]:
                df.at[i, df.columns[7]] = scrape_df[df_columns][weather_array[0][1]]
            if weather_array[1][2] == df.columns[8]:
                df.at[i, df.columns[8]] = scrape_df[df_columns][weather_array[0][2]]
    

    #print(df_columns)
    # df = pd.DataFrame({'temp': scrape_df[df_columns][weather_array[0][0]]}, index = [1])
    # df['wind_speed'] = scrape_df[df_columns][weather_array[0][1]]
    # df['total_rain'] = scrape_df[df_columns][weather_array[0][2]]

    # for i in range(len(weather_array[0])):
    #     if (weather_array[1][i]) == (df[i].columns.name):
    #         df[i] = df[scrape_df[df_columns][weather_array[0][i]]]
    #         #pd.DataFrame({weather_array[1][i]: [scrape_df[df_columns][weather_array[0][i]]]})
    #         print(df[i])
        #return df
    # df_list = pd.read_html(response)[0]
    # df_list.reset_index()
    # print(df_list.columns)
    # print(df)
    # return df


if __name__ == '__main__':
    parse_weather()
    parse_info()
    parse_status()
    print(df)
    #print(df.dtypes)
    #parse_json()
    #print(df.head(5))