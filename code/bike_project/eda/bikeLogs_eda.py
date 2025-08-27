import sqlite3
import pandas as pd
import numpy as np
import datetime as dt
import time
from datetime import datetime
import pytz

conn = sqlite3.connect('../data/bikeLogs_backup.db')

query = "SELECT * FROM bike_logs"

df_raw = pd.read_sql(query, conn)

# filling missing is_semester and is_weekend values with proper values
# precipitation and bikes_available set to 0 for any null values 
#station_id|num_bikes_available|temp|wind_speed|campus_rain|precipitation|dttime

# converting datatypes
df_raw['num_bikes_available'] = df_raw['num_bikes_available'].astype(int)
df_raw['date_time'] = pd.to_datetime(df_raw.dttime, format='%y%m%d%H%M%S')
df_raw.drop(columns=['dttime'],inplace = True)
local_timezone = pytz.timezone('America/Denver')
df_raw['date_time'] = pd.to_datetime(df_raw['date_time'].dt.tz_localize('UTC').dt.tz_convert(local_timezone))
df_raw['date_time'] = df_raw['date_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
df_raw['date_time'] = pd.to_datetime(df_raw['date_time'])

# local_timezone = pytz.timezone('America/Denver')
df_raw['time'] = df_raw['date_time'].dt.strftime("%H:%M:%S")
df_raw['date'] = df_raw['date_time'].dt.strftime('%Y-%m-%d')
df_raw['date']= pd.to_datetime(df_raw['date'])

# df_raw['converted_date_time'] = df_raw['date_time'].dt.tz_localize('UTC').dt.tz_convert(local_timezone)
#copy of raw cleaned data frame
df_eda = df_raw.copy()
# df_eda = df_eda.sort_values(by=['date','time'], ascending=[False, False])


def calculate_release(df):
    # release_df = pd.DataFrame({
    #     'station_id':pd.Series([], dtype = 'object'),
    #     'date':pd.Series([], dtype = 'object'), 
    #     'time':pd.Series([], dtype = 'object'), 
    #     'day_of_week':pd.Series([], dtype = 'object'), 
    #     'output':pd.Series([], dtype = 'object'), 
    # })

    df['day_of_week'] = df['date'].dt.day_name()

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
        True
    ]
    df['is_release'] = np.select(conditions, choices, default=False)

    df.drop(columns=['day_of_week'],inplace = True)
    df.drop(columns=['date'],inplace = True)
    df.drop(columns=['time'],inplace = True)
    # end = time.time()
    # print("release:", end - start)
    return df['is_release']

def calculate_pickups(df):
    #start = time.time()

    df['curr'] = df['bikes_available']

    #index = pickups_df['station_id'].nunique()
    #pickups_df['prev'] = pickups_df['bikes_available'].shift(periods = index, fill_value = 0)
    df['prev'] = df.groupby('station_id')['bikes_available'].shift(fill_value = 0)

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

    # end = time.time()
    # print("pickups:", end - start)
    return df['pickups']

# may want to shift by 5 as value changes every 5 min
# also should make sure that it resets every day, just by only returning 0 if value is negative 
# otherwise good i think
def calculate_precipitation(df):
    df['curr'] = df['ss_precipitation']
    df['prev'] = df.groupby('station_id')['ss_precipitation'].shift(periods=5, fill_value = 0)
    df['difference'] = df['prev'] - df['curr']
    
    conditions_1 = [
        (df['temp'] <= 32),
        (df['temp'] > 32)
    ]
    choices_1 = [
        df['fw_precipitation'], 
        df['difference']
    ]
    df['precipitation'] = np.select(conditions_1, choices_1)

    conditions_2 = [
        (df['precipitation'] > 0)
    ]
    choices_2 = [
        1
    ]
    df['is_precipitation'] = np.select(conditions_2, choices_2, default=0) 

    df.drop(columns=['curr'],inplace = True)
    df.drop(columns=['prev'],inplace = True)
    df.drop(columns=['difference'],inplace = True)
    df.drop(columns=['precipitation'],inplace = True)

    return df['is_precipitation']


if __name__ == '__main__':
    # print(df_bikes.head(20))
    print(df_raw.head(10))
    print(calculate_release(df_raw))

    #print(df_eda)
    # test_two = calculate_release()
    # print(test_two.head(10))