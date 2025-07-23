import requests
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd

# boulder_weather = https://api.weather.gov/gridpoints/BOU/54,74/forecast/hourly
weather_url = "https://sundowner.colorado.edu/weather/atoc1/"
bcycle_url = "https://gbfs.bcycle.com/bcycle_boulder/"

main_df = pd.DataFrame(columns=['station_id', 'name', 'lon', 'lat', 'lon', 'num_docks_available', 'num_bikes_available', 'temp', 'wind_speed', 'total_rain'])

request_names = [
    'station_information',
    'station_status'
]

station_array = np.array([0, 14, 19, 29, 34, 35, 37, 40, 42, 44, 47, 52, 53])

info_columns = [
    'lat',
    'lon',
    'name',
    'station_id'
]

status_columns = [
    'num_docks_available',
    'num_bikes_available'
]

# if bcycle_json:
#     for i in range(len(station_array)):
#         for j in range(len(status_columns)):
#             print(station_array[i], "==", bcycle_json["data"]["stations"][station_array[i]][status_columns[j]])
        # print("index:", station_array[i], bcycle_info["data"]["stations"][station_array[i]]["name"])
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
                        print(station_array[j], "==", bcycle_json["data"]["stations"][station_array[j]][info_columns[k]])
                if i == 1:
                    for k in range(len(status_columns)):
                        print(station_array[j], "==", bcycle_json["data"]["stations"][station_array[j]][status_columns[k]])

weather_array = np.array([[0,5,8],
                         ['temp', 'wind speed', 'total rain']], dtype=object)

def get_weather_df(index):
    url = weather_url
    response = requests.get(url)

    if response.status_code == 200:
        content = response.content
        df = pd.read_html(content)[index]
        return df
    else:
        print(f"Failed to retrive data {response.status_code}")

def scrape(df):
    scrape_df = get_weather_df(0)
    df_columns = scrape_df.columns[1]

    #print(df_columns)
    df = pd.DataFrame({'temp': scrape_df[df_columns][weather_array[0][0]]}, index = [1])
    df['wind_speed'] = scrape_df[df_columns][weather_array[0][1]]
    df['total_rain'] = scrape_df[df_columns][weather_array[0][2]]
    # for i in range(len(weather_array[0])):
    #     print(weather_array[1][i], "==", scrape_df[df_columns][weather_array[0][i]])
    # df_list = pd.read_html(response)[0]
    # df_list.reset_index()
    # print(df_list.columns)
    print(df)
    return df

if __name__ == '__main__':
    scrape(main_df)
    #parse_json()
    #print(main_df.head(5))