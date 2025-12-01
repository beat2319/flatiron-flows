import requests
import pandas as pd
import datetime as dt
import numpy as np
import sqlite3
import logging
import os
import lxml # Kept this as it is required by read_html backend
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv('.env')
WEBHOOK_URL = os.getenv('ERROR_WEBHOOK')

# Paths & URLs
# Using your exact absolute path - vital for cronjobs to find the DB
DB_PATH = '/usr/src/app/data/bike_logs.db' 

BCYCLE_URL_BASE = "https://gbfs.bcycle.com/bcycle_boulder/"
WEATHER_URL = "https://sundowner.colorado.edu/weather/atoc1/"
PRECIP_URL = "https://api.open-meteo.com/v1/forecast?latitude=40.0073&longitude=-105.2660&current=precipitation"

# The 7 stations from your original array
TARGET_STATION_IDS = [
    "bcycle_boulder_1855", "bcycle_boulder_2132", "bcycle_boulder_2756", 
    "bcycle_boulder_2767", "bcycle_boulder_3318", "bcycle_boulder_2144", 
    "bcycle_boulder_1872"
]

# Configure logging to show timestamps
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_discord_alert(message, status_code):
    """Sends an error message to Discord."""
    if not WEBHOOK_URL:
        logging.warning(f"Error ({status_code}): {message} (No Webhook configured)")
        return

    data = {
        "content": f"Script Error: {message}",
        "username": f"Error Bot {status_code}",
    }
    try:
        requests.post(WEBHOOK_URL, json=data, timeout=10)
    except Exception as e:
        logging.error(f"Failed to send Discord alert: {e}")

def get_bcycle_data():
    """Fetches B-Cycle data and returns a DataFrame of target stations."""
    try:
        # 1. Get Static Info (IDs)
        info_resp = requests.get(f"{BCYCLE_URL_BASE}station_information")
        if info_resp.status_code != 200:
            send_discord_alert("B-Cycle Info Failed", info_resp.status_code)
            return pd.DataFrame()
            
        info_df = pd.DataFrame(info_resp.json()['data']['stations'])
        
        # 2. Get Live Status (Bikes available)
        status_resp = requests.get(f"{BCYCLE_URL_BASE}station_status")
        if status_resp.status_code != 200:
            send_discord_alert("B-Cycle Status Failed", status_resp.status_code)
            return pd.DataFrame()
            
        status_df = pd.DataFrame(status_resp.json()['data']['stations'])

        # 3. Merge securely on station_id
        full_df = pd.merge(info_df[['station_id']], 
                           status_df[['station_id', 'num_bikes_available']], 
                           on='station_id')
        
        # 4. Filter for only the stations we want
        target_df = full_df[full_df['station_id'].isin(TARGET_STATION_IDS)].copy()
        target_df.reset_index(drop=True, inplace=True)
        return target_df

    except Exception as e:
        logging.error(f"B-Cycle logic failed: {e}")
        return pd.DataFrame()

def get_weather_values():
    """Scrapes the CU weather table using your original read_html logic."""
    try:
        response = requests.get(WEATHER_URL)
        if response.status_code != 200:
            send_discord_alert("Weather Page Failed", response.status_code)
            return {'temp': np.nan, 'wind_speed': np.nan, 'campus_rain': np.nan}

        # Original scraping logic preserved
        content = response.content
        scrape_df = pd.read_html(content)[0]
        
        # Grab column 1 (data values) and specific rows as per your original array
        target_col_name = scrape_df.columns[1]
        
        return {
            'temp': scrape_df[target_col_name][0],       # Row 0
            'wind_speed': scrape_df[target_col_name][5], # Row 5
            'campus_rain': scrape_df[target_col_name][8] # Row 8
        }
    except Exception as e:
        logging.error(f"Weather parsing failed: {e}")
        return {'temp': np.nan, 'wind_speed': np.nan, 'campus_rain': np.nan}

def get_precipitation():
    """Fetches precipitation from Open-Meteo."""
    try:
        response = requests.get(PRECIP_URL)
        if response.status_code != 200:
            send_discord_alert("Precip API Failed", response.status_code)
            return np.nan
            
        data = response.json()
        return data["current"]["precipitation"]
    except Exception as e:
        logging.error(f"Precipitation logic failed: {e}")
        return np.nan

def save_to_database(df):
    """Saves the dataframe to SQLite using your original logic."""
    conn = None
    try:
        # Check if directory exists (Crucial for cronjobs)
        db_dir = os.path.dirname(DB_PATH)
        if not os.path.exists(db_dir):
            logging.warning(f"Directory {db_dir} does not exist. Creating it.")
            os.makedirs(db_dir, exist_ok=True)

        conn = sqlite3.connect(DB_PATH)
        
        # Use your original to_sql logic
        df.to_sql(name='bike_logs', con=conn, if_exists='append', index=False)
        logging.info(f"Successfully logged {len(df)} rows to {DB_PATH}")
        
    except Exception as e:
        logging.error(f"Database write failed: {e}")
        send_discord_alert("Database Write Failed", 500)
    finally:
        if conn:
            conn.close()

def main():
    # 1. Build the base dataframe from B-Cycle data
    df = get_bcycle_data()
    
    if df.empty:
        logging.warning("No B-Cycle data found. Skipping run.")
        return

    # 2. Fetch environmental data ONCE
    weather_data = get_weather_values()
    precip_value = get_precipitation()
    current_time = dt.datetime.now()

    # 3. Apply values to all rows
    df['temp'] = weather_data['temp']
    df['wind_speed'] = weather_data['wind_speed']
    df['campus_rain'] = weather_data['campus_rain']
    df['precipitation'] = precip_value
    df['dttime'] = current_time

    # 4. Reorder columns to match your original schema exactly
    # Original: station_id, num_bikes_available, temp, wind_speed, campus_rain, precipitation, dttime
    final_cols = ['station_id', 'num_bikes_available', 'temp', 'wind_speed', 'campus_rain', 'precipitation', 'dttime']
    
    # Ensure all columns exist (in case of partial API failure)
    for col in final_cols:
        if col not in df.columns:
            df[col] = np.nan

    df_final = df[final_cols]
    
    # 5. Print to logs/stdout (useful for cron logs)
    print(df_final.head())

    # 6. Save to SQLite
    save_to_database(df_final)

if __name__ == '__main__':
    main()