import sqlite3
import pandas as pd
import numpy as np
import pytz
from pandas.tseries.holiday import USFederalHolidayCalendar as calendar

def load_data(db_path, query):
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql(query, conn)
    return df
# conn = sqlite3.connect('../../data/bikeLogs_backup.db')

# query = "SELECT * FROM bike_logs"

# df_raw = pd.read_sql(query, conn)

def convert_datetime(df_in):
    df = df_in.copy()
    
    df['dttime'] = pd.to_datetime(df['dttime'])
    local_timezone = pytz.timezone('America/Denver')

    df['date_time'] = df['dttime'].dt.tz_localize('UTC').dt.tz_convert(local_timezone)
    df['date_time'] = pd.to_datetime(df['date_time'].dt.strftime('%Y-%m-%d %H:%M:%S'))
    df['date'] = df['date_time'].dt.date
    df['min'] = df['date_time'].dt.minute
    # df['modFive_min'] = df['min'].mod(5)
    df['day_of_week'] = df['date_time'].dt.day_name()

    df = df.drop(columns=['dttime', 'min'])
    return df

# def filter_to_five_min_intervals(df_in):
#     df = df_in[df_in['modFive_min'] == 0].copy()
#     df = df.drop(columns=['modFive_min'])
#     return df

def calculate_release(df_in):
    df = df_in.copy()

    mwf_start_times = [
        '08:50', '09:55', '11:00', '12:05', '13:10',
        '14:15', '15:20', '16:25', '17:30', '18:35'
    ]
    
    tt_start_times = [
        '09:15', '10:45', '12:15', '13:45',
        '15:15', '16:45', '18:15'
    ]

    df = df.set_index('date_time')

    release_mask = pd.Series(False, index=df.index)

    is_mwf = df['day_of_week'].isin(['Monday', 'Wednesday', 'Friday'])
    is_tt = df['day_of_week'].isin(['Tuesday', 'Thursday'])
    
    time_str = df.index.strftime('%H:%M')

    is_mwf_time = pd.Series(time_str).isin(mwf_start_times).values
    is_tt_time = pd.Series(time_str).isin(tt_start_times).values
        
    release_mask = (is_mwf & is_mwf_time) | (is_tt & is_tt_time)
        
    df['is_release'] = release_mask.astype(int)
    
    df = df.reset_index()
    return df

def calculate_pickups(df_in):
    df = df_in.copy()

    df['num_bikes_available'] = pd.to_numeric(df['num_bikes_available'])

    df = df.sort_values(by=['station_id', 'date_time'])

    df['prev_bikes'] = df.groupby('station_id')['num_bikes_available'].shift(fill_value=np.nan)

    df['difference'] = df['prev_bikes'] - df['num_bikes_available']

    df['pickups'] = df['difference'].clip(lower=0).fillna(0).astype(int)

    df = df.drop(columns=['prev_bikes', 'difference'])
    return df

def calculate_avaliablity(df_in):
    df = df_in.copy()

    df['num_bikes_available'] = pd.to_numeric(df['num_bikes_available'])

    df = df.sort_values(by=['station_id', 'date_time'])

    df['num_bikes_available_mean'] = pd.mean(df['num_bikes_available'])
    df['num_bikes_available_min']


def calculate_precipitation(df_in):
    df = df_in.copy()

    df = df.sort_values(by=['station_id', 'date_time'])
    
    df['prev_rain'] = df.groupby('station_id')['campus_rain'].shift(periods=1, fill_value=0)
    df['rain_diff'] = df['campus_rain'] - df['prev_rain']

    df['calculated_precipitation'] = np.where(
        df['temp'] <= 32,
        df['precipitation'],
        df['rain_diff']
    )
    
    df['is_precipitation'] = (df['calculated_precipitation'] > 0).astype(int)

    df = df.drop(columns=['prev_rain', 'rain_diff', 'calculated_precipitation', 
                          'campus_rain', 'precipitation'])
    return df

def calculate_holiday(df_in):
    df = df_in.copy()

    start_date = df['date'].min()
    end_date = df['date'].max()

    cal = calendar()
    holidays = cal.holidays(start_date, end_date)

    df['is_holiday'] = df['date'].isin(holidays).astype(int)
    
    df = df.drop(columns=['date'])
    return df

def group_by_hour(df_in):
    df = df_in.copy()

    df['temp'] = pd.to_numeric(df['temp'], errors='coerce')

    hourly_df = df.groupby(['station_id', pd.Grouper(key="date_time", freq="1h")]).agg(
        pickups =('pickups', 'sum'),
        is_release =('is_release', 'max'), 
        is_precipitation =('is_precipitation', 'max'),
        is_holiday = ('is_holiday', 'max'), 
        day_of_week = ('day_of_week', 'first'), 
        temp = ('temp', 'mean'),
        wind_speed = ('wind_speed', 'mean')
    )

    hourly_df = hourly_df.reset_index()
    return hourly_df

def resample_to_five_min(df_in):
    df = df_in.copy()
    
    # aggregation_rules = {
    #     'station_id': 'first',
    #     'day_of_week': 'first',

    #     'pickups': 'sum', 

    #     'num_bikes_available': ['mean', 'min'], 

    #     'campus_rain': 'last', 
    #     'precipitation': 'last',
    #     'temp': 'last', 

    #     'wind_speed': 'mean', 
    #     'is_release': 'max',  
    #     'is_holiday': 'max'
    # }
    
    df_5min = df.groupby(['station_id', pd.Grouper(key="date_time", freq="5min")]).agg(
        station_id = ('station_id', 'first'),
        pickups = ('pickups', 'sum'),
        is_release =('is_release', 'max'), 
        precipitation =('precipitation', 'max'),
        campus_rain =('campus_rain', 'max'),
        bikes_avaliable_min = ('num_bikes_available', 'min'),
        bikes_avaliable_mean = ('num_bikes_available', 'mean'),
        is_holiday = ('is_holiday', 'max'), 
        day_of_week = ('day_of_week', 'first'), 
        temp = ('temp', 'mean'),
        wind_speed = ('wind_speed', 'mean')
    )
    # new_cols = [
    #     col[0] if col[1] in ['first', 'last']  
    #     else f"{col[0]}_{col[1]}"               
    #     for col in df_5min.columns.values
    # ]

    # df_5min = df_5min.rename(columns={
    #     'pickups_sum': 'pickups',
    #     'is_release_max': 'is_release',
    #     'is_holiday_max': 'is_holiday',
    # })

    # df_5min.columns = new_cols
    
    if 'station_id' in df_5min.columns:
        df_5min = df_5min.drop(columns=['station_id'])
    
    return df_5min.reset_index()

def main():
    DB_PATH = '../../data/db/bikeLogs_backup.db'
    QUERY = "SELECT * FROM bike_logs"
    
    df = load_data(DB_PATH, QUERY)
    

    df_1min = (df
        .pipe(convert_datetime)  
        .pipe(calculate_release)
        .pipe(calculate_pickups) 
        .pipe(calculate_holiday)
    )


    df_5min = df_1min.pipe(resample_to_five_min)

    df_processed = df_5min.pipe(calculate_precipitation)

    df_hourly = group_by_hour(df_processed)

    print("\n--- 5-minute ---")
    print(df_processed.tail(50))
    
    print("\n--- Hourly  ---")
    print(df_hourly.head(20))

    with sqlite3.connect('../../data/db/bikeLogs_1hr.db') as conn:
        df_hourly.to_sql('bike_logs', con=conn, if_exists='replace', index=False)

if __name__ == '__main__':
    main()