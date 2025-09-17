import sqlite3
import pandas as pd
import numpy as np
import datetime as dt
import time
import timeit
import pytz

conn = sqlite3.connect('../../data/bike_logs.db')

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



def calculate_release(df):
    df['time'] = df['date_time'].dt.strftime("%H:%M:%S")
    df['date'] = df['date_time'].dt.strftime('%Y-%m-%d')
    df['date']= pd.to_datetime(df['date'])

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

    # going to do major work soon, need to clean up the np.select mess (with full respect to how quick it is)

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
        1
    ]
    df['is_release'] = np.select(conditions, choices, default=0)

    df.drop(columns=['date'],inplace = True)
    df.drop(columns=['time'],inplace = True)
    return df['is_release']

def calculate_pickups(df):
    df['num_bikes_available'] = df['num_bikes_available'].astype(int)

    df['curr'] = df['num_bikes_available']
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

    df['pickups'] = np.select(conditions, choices)
    
    df.drop(columns=['curr'],inplace = True)
    df.drop(columns=['prev'],inplace = True)
    df.drop(columns=['difference'],inplace = True)
    df.drop(columns=['num_bikes_available'],inplace = True)
    return df['pickups']

# may want to shift by 5 as value changes every 5 min
# also should make sure that it resets every day, just by only returning 0 if value is negative 
# otherwise good i think
def calculate_precipitation(df):
    df['curr'] = df['campus_rain']
    df['prev'] = df.groupby('station_id')['campus_rain'].shift(periods=5, fill_value = 0)
    df['difference'] = df['curr'] - df['prev']
    
    conditions_1 = [
        (df['temp'] <= 32),
        (df['temp'] > 32)
    ]
    choices_1 = [
        df['precipitation'], 
        df['difference']
    ]
    df['calculated_precipitation'] = np.select(conditions_1, choices_1)

    conditions_2 = [
        (df['calculated_precipitation'] > 0)
    ]
    choices_2 = [
        1
    ]
    df['is_precipitation'] = np.select(conditions_2, choices_2, default=0) 

    df.drop(columns=['curr'],inplace = True)
    df.drop(columns=['prev'],inplace = True)
    df.drop(columns=['difference'],inplace = True)
    df.drop(columns=['calculated_precipitation'],inplace = True)
    df.drop(columns=['campus_rain'],inplace = True)
    df.drop(columns=['precipitation'],inplace = True)
    return df['is_precipitation']


if __name__ == '__main__':
    convert_datetime(df_eda)
    calculate_release(df_eda)
    calculate_precipitation(df_eda)
    calculate_pickups(df_eda)

    print(f"\n release_period: \n {df_eda.query('is_release == 1')}")
    print(f"\n precipitation: \n {df_eda.query('is_precipitation == 1')}")
    # test_two = calculate_release()
    # print(test_two.head(10))