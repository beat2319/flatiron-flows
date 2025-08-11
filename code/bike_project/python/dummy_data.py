import pandas as pd
import numpy as np
import time

df = pd.DataFrame({
    'station_id':pd.Series(['one', 'two', 'three', 'four', 'five'] * 6), 
    'temp':pd.Series(np.random.randint(1,80,30)),  
    'campus_rain':pd.Series([1]*30),
    'precipitation': pd.Series([0]*30),
})

def calculate_precipitation():
    start = time.time()
    precipitation_df = pd.DataFrame({
        'station_id':pd.Series([], dtype = 'object'),
        'temp':pd.Series([], dtype = 'object'), 
        'summer_precip':pd.Series([], dtype = 'object'), 
        'winter_precip':pd.Series([], dtype = 'object'), 
        'output':pd.Series([], dtype = 'object'), 
    })
    precipitation_df['station_id'] = df['station_id']
    precipitation_df['temp'] = df['temp']
    precipitation_df['summer_precip'] = df['campus_rain']
    precipitation_df['winter_precip'] = df['precipitation']

    conditions = [
        (precipitation_df['temp'] <= 32),
        (precipitation_df['temp'] > 32)
    ]
    choices = [
        precipitation_df['winter_precip'], 
        precipitation_df['summer_precip']
    ]
    precipitation_df['output'] = np.select(conditions, choices)
    end = time.time()
    print("pickups:", end - start)
    return precipitation_df

if __name__ == '__main__':
    test_df = calculate_precipitation()
    print(test_df.head(40))
    conn = sqlite3.connect 