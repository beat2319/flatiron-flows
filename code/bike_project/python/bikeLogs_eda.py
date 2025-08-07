import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import time

connection = sqlite3.connect('../../data/bike_logs.db')

query = "SELECT * FROM logs WHERE is_semester = 1 OR is_semester is NULL ORDER BY date ASC"

df = pd.read_sql(query, connection)

# filling missing is_semester and is_weekend values with proper values
# precipitation and bikes_available set to 0 for any null values 
values = {"bikes_available": 0, "docks_available": 0, "is_semester": 1, "is_weekend": 0, "precipitation": 0}
df = df.fillna(value = values)

# converting datatypes
df['bikes_available'] = df['bikes_available'].astype(int)
df['docks_available'] = df['docks_available'].astype(int)
df['date'] = pd.to_datetime(df['date'])
df['is_semester'] = df['is_semester'].astype(int)
df['is_weekend'] = df['is_weekend'].astype(int)
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

# using numpy.select to statically "loop" through the day_of_week and time dataframes 
# columns and compare with mwf_time, tt_time, and weekdays respecively
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

df['release_period'] = np.select(conditions, choices, default=False)

# df_val = df['station_id']
# print(df.loc[:'bcycle_boulder_1855'].head(12))
# print(df.cell.get_loc('bcycle_boulder_1855'))

# instead make new column, it will be a changed index on stat ion_id column (n-1)
#df.index = pd.RangeIndex(start=1, stop=600, step=1)
# df['station_id_two'] = df['station_id']

# df.set_index([pd.RangeIndex(start=0, stop=26622, step=13), 'station_id_two'])
# make a pivot table of the columns (for station_id) rows can (bikes_available & bikes_available_two) be pickups 
# make a pivot table of the columns (for station_id) rows can (drops_available & drops_available_two) be dropoffs 
# make a df for each row of station_id, columns remain the same

# instead calculate the mod of each station (index mod 13 = [0 thru 12])
# then change the index to start at 13 and do the same mod calulation
# subtract the two columns from each other the result will be the pickups or dropoffs

# we have to make a separate dataframe that will first contain prev_bikes_available 
# bikes_available transposed (first 13 columns removed)

# deletes the intial rows
# def curr(df_column, value):
#     start = time.time()
#     df_curr = df_column
#     # df_curr_t = df_curr.T

#     # for i in range(value):
#     #     df_curr_t.pop(i)

#     # df_curr = df_curr_t.T
#     #df_curr = df_curr.shift(periods = -13)
#     #df_prev = df_prev.set(drop=True) 
#     # print (df_name.head(10))
#     end = time.time()
#     print(end - start)  
#     return df_curr

# deletes final rows
# def prev(df_column, value):
#     df_prev = df_column
#     # df_prev_t = df_prev.T

#     # index = ((len(df_prev)) - (value))
#     # # # print(index)

#     # for i in range(value):
#     #     df_prev_t.pop(index + i)

#     # df_prev = df_prev.reindex(13) 
#     # df_prev = df_prev_t.T
#     # print (df_name.head(10))

#     df_prev = df_prev.shift(periods = value, fill_value = 0)
#     return df_prev
# create new dataframe
# add curr and prev columns to dataframe
# pop both
# calculate the difference and return as column

def calculate_diff(df_column, value):
    new_df = pd.DataFrame({
    'station_id':pd.Series([], dtype = 'object'),
    'input':pd.Series([], dtype = 'object'), 
    'prev':pd.Series([], dtype = 'object'), 
    'curr':pd.Series([], dtype = 'object'), 
    'output':pd.Series([], dtype = 'object'), 
    })

    new_df['station_id'] = df['station_id']
    
    new_df['input'] = df_column

    new_df['curr'] = new_df['input']
    #new_df['curr'] = new_df[['curr']].infer_objects().fillna(0)

    new_df['prev'] = new_df['input'].shift(periods = value, fill_value = 0)
    #new_df['prev'] = new_df[['prev']].infer_objects().fillna(0)

    new_df['output'] = new_df['prev'] - new_df['curr']
    new_df['output'] = new_df[['output']].infer_objects().fillna(0)
    new_df['output'] = new_df['output'].astype(int)

    conditions = [(new_df['output'] <= 0),
                  (new_df['output'] > 0)]
    choices = [0, new_df['output']]
    new_df['output'] = np.select(conditions, choices)

    return new_df['output']

# print(df['station_id_two'].head(10), df['station_id'].head(10))

# print(df.index.get_loc(df[df['station_id'] == 'bcycle_boulder_1855'].index[1]))
# print(df.loc[0, "bikes_available"])


if __name__ == '__main__':
    # start = time.time()
    # print(df_bikes.head(20))
    test_df = calculate_diff(df['bikes_available'], 13)
    print(test_df.head(20))
      
    #df['dropoffs'] = calculate_diff(df['docks_available'], 13)
    # print(df)

    # prev_bikes_avaliable = remove_curr(df['bikes_available'], 13)
    # print(prev_bikes_avaliable.head(10))
    # # want_in = (len(df['bikes_available']))
    # curr_bikes_avaliable = calculate_diff 
    # print(curr_bikes_avaliable.head(10))
    #print(test_df.head(10))
    #print(df['bikes_available'].tail(10))
# using pandas apply and lambda to apply specific function to the dataframe         
# df['release_period'] = df.apply(lambda x: isRelease(x['day_of_week'], x['time']), axis=1)

#print(list(df))
#print(df.query('release_period == True').head(50))
#print(df.query('release_period == True').tail(50))
#print(df)