import sqlite3
import pandas as pd
import numpy as np
import datetime as dt
import time
import timeit
import pytz
from sqlalchemy import create_engine, text

conn = sqlite3.connect('../data/bikeLogs_backup.db')

query = "SELECT * FROM bike_logs"

df_raw = pd.read_sql(query, conn)

df_eda = pd.DataFrame({
    'station_id':pd.Series([], dtype = 'object'), 
    'num_bikes_available':pd.Series([], dtype = 'object'),
    'temp':pd.Series([], dtype = 'object'),  
    'wind_speed':pd.Series([], dtype = 'object'),  
    'campus_rain':pd.Series([], dtype = 'object'),
    'precipitation': pd.Series([], dtype = 'object'),
    'dttime':pd.Series([], dtype = 'object'),

    'modFive_min':pd.Series([], dtype = 'object'),
    'min':pd.Series([], dtype = 'object'),

    'date_time':pd.Series([], dtype = 'object'),
    'day_of_week':pd.Series([], dtype = 'object'),
    'calculated_precipitation':pd.Series([], dtype = 'object'),
    'is_precipitation':pd.Series([], dtype = 'object'),
})

df_eda = df_raw
# converting datatypes
# df_eda['num_bikes_available'] = df_eda['num_bikes_available'].astype(int)

def convert_datetime(df):
    df['dttime'] = pd.to_datetime(df_eda['dttime'])  
    local_timezone = pytz.timezone('America/Denver')
    df['dttime'] = pd.to_datetime(df['dttime'].dt.tz_localize('UTC').dt.tz_convert(local_timezone))

    df['date_time'] = df['dttime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['date_time'] = pd.to_datetime(df['date_time'])

    df['min'] = df['date_time'].dt.minute
    df['modFive_min'] = df['min'].mod(5)

    df['day_of_week'] = df['date_time'].dt.day_name()

    df.drop(columns=['dttime'],inplace = True)
    return (df['date_time'], df['day_of_week'])

# df_eda['curr_time'] = df_eda['dttime'].total_seconds()
# df_eda['prev_time'] = df_eda['curr_time'].shift(fill_value = 0).astype(int)
# df_eda['result_time'] = df_eda['curr_time'] - df_eda['prev_time']

# df_raw['converted_date_time'] = df_raw['date_time'].dt.tz_localize('UTC').dt.tz_convert(local_timezone)
# copy of raw cleaned data frame
# df_eda = df_raw.copy()
# df_eda = df_eda.sort_values(by=['date','time'], ascending=[False, False])

# may want to shift by 5 as value changes every 5 min
# also should make sure that it resets every day, just by only returning 0 if value is negative 
# otherwise good i think

def modFive_calc(df):
    val = df[df['modFive_min'] == 0].index[0]
    df_drop_index = df.index[:val]

    df.drop(columns=['modFive_min'],inplace = True)
    df.drop(columns=['min'],inplace = True)
    return df_drop_index

def remove_rows(df):
    print(f"before: {len(df)}")
    df.drop(modFive_calc(df), inplace = True)
    print(f"after: {len(df)}")

def calculate_precipitation(df):
    df['campus_rain'] = df['campus_rain']
    print(df['campus_rain'])
    # # df['curr'] = df.groupby('modFive_min')['campus_rain']
    # print(df.head())
    # df['prev'] = df.groupby('station_id')['campus_rain'].shift(periods=5, fill_value = 0)
    # df['difference'] = df['curr'] - df['prev']

    # conditions_1 = [
    #     (df['temp'] <= 32),
    #     (df['temp'] > 32)
    # ]
    # choices_1 = [
    #     df['precipitation'], 
    #     df['difference']
    # ]
    # df['calculated_precipitation'] = np.select(conditions_1, choices_1)

    # conditions_2 = [
    #     (df['calculated_precipitation'] > 0)
    # ]
    # choices_2 = [
    #     1
    # ]
    # df['is_precipitation'] = np.select(conditions_2, choices_2, default=0) 

    # df.drop(columns=['curr'],inplace = True)
    # df.drop(columns=['prev'],inplace = True)
    # df.drop(columns=['difference'],inplace = True)
    # df.drop(columns=['calculated_precipitation'],inplace = True)
    # df.drop(columns=['campus_rain'],inplace = True)
    # df.drop(columns=['precipitation'],inplace = True)
    # return df['calculated_precipitation']


if __name__ == '__main__':
    convert_datetime(df_eda)
    # calculate_precipitation(df_eda)
    remove_rows(df_eda)

    # print(modFive_calc(df_eda))
    # print(f"\n first index: \n {df_eda.query('modFive_min == 0')}")

    # connTwo = sqlite3.connect('../../data/bikeLogs_eda.db')

    # df_eda.to_sql('bike_logs',
    #            con=connTwo)

    # print(f"\n release_period: \n {df_eda.query('is_release == 1')}")
    # print(f"\n precipitation: \n {df_eda.query('is_precipitation == 1')}")
    # test_two = calculate_release()
    # print(test_two.head(10))