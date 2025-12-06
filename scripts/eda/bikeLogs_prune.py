import sqlite3
import pandas as pd
import numpy as np

def load_data(db_path, query):
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql(query, conn)
    return df

def int_embbed(df_in):
    df = df_in.copy()

    conditions = [df['station_id'] == 'bcycle_boulder_2144', df['station_id'] == 'bcycle_boulder_1872', df['station_id'] == 'bcycle_boulder_1855', df['station_id'] == 'bcycle_boulder_2132', df['station_id'] == 'bcycle_boulder_2756', df['station_id'] == 'bcycle_boulder_2767', df['station_id'] == 'bcycle_boulder_3318']
    choices = [0,1,2,3,4,5,6]
    df['station_int'] = np.select(conditions, choices)

    return df

def filter_stations(df_in):
    df = df_in.copy()
    target = ['bcycle_boulder_2144', 'bcycle_boulder_1872', 'bcycle_boulder_1855', 'bcycle_boulder_2132', 'bcycle_boulder_2756', 'bcycle_boulder_2767', 'bcycle_boulder_3318']
    df = df[df['station_id'].isin(target)]

    return df


def main():
    DB_PATH = '../../data/db/bikeLogs_dropoff.db'
    QUERY = "SELECT * FROM bike_logs"
    
    df = load_data(DB_PATH, QUERY)
    filtered_df = df.pipe(filter_stations)
    monthly_station = filtered_df.pipe(int_embbed)

    monthly_station.to_csv("../../data/csv/monthly/bikeLogs_monthly_stations.csv", index=False)

if __name__ == '__main__':
    main()
