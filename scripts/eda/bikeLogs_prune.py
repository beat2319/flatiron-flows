import sqlite3
import pandas as pd
import numpy as np

def load_data(db_path, query):
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql(query, conn)
    return df

def main():
    DB_PATH = '../../data/db/bikeLogs_Month.db'
    QUERY = "SELECT * FROM bike_logs"
    
    df = load_data(DB_PATH, QUERY)
    bcycle_boulder_1855 = df[df['station_id'] == 'bcycle_boulder_1855']
    print(df.head(10))
    print(bcycle_boulder_1855)
    bcycle_boulder_1855.to_csv("../../data/csv/bikeLogs_1885.csv", index=False)

if __name__ == '__main__':
    main()
