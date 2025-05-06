import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta

# --- Configuration ---
# --- >>> Path to your specific database <<< ---
db_path = "/Users/benatkinson/Library/Mobile Documents/com~apple~CloudDocs/School/3rd_Year/Semester_1/GEOG_3023/flatiron-flows/data/bike_logs.db"

# --- >>> Path to the LATEST CSV with 24-hour format and threshold <<< ---
processed_precip_csv = "open-meteo-15min-precip-thresh-24hr.csv"

# --- 1. Load the Pre-Processed 15-Minute Precipitation Data ---
print(f"Loading 15-minute precipitation data from: {processed_precip_csv}")
if not os.path.exists(processed_precip_csv):
    print(f"Error: Processed precipitation file not found at {processed_precip_csv}")
    exit()

try:
    precip_df = pd.read_csv(processed_precip_csv)
    # Ensure columns exist
    if not {'date_key', 'time_key', 'precipitation_15min_mm'}.issubset(precip_df.columns):
        print("Error: CSV file is missing one or more required columns: 'date_key', 'time_key', 'precipitation_15min_mm'")
        print("Columns found:", precip_df.columns.tolist())
        exit()

    # Convert precip to numeric just in case
    precip_df['precipitation_15min_mm'] = pd.to_numeric(precip_df['precipitation_15min_mm'], errors='coerce')
    precip_df = precip_df.dropna(subset=['precipitation_15min_mm']) # Drop rows where precip is not numeric

    print(f"Loaded {len(precip_df)} rows of 15-minute precipitation data.")
    # Optional: Check data
    # print(precip_df.head())
    # print(precip_df.info())

except Exception as e:
    print(f"Error loading or processing precipitation CSV: {e}")
    exit()

# --- 2. Connect to the SQLite Database ---
print(f"Connecting to database: {db_path}")
if not os.path.exists(db_path):
    print(f"Error: Database file not found at {db_path}")
    exit()

conn = None # Initialize connection variable
try:
    # --- >>> REMINDER: Make a backup of the DB at db_path before running! <<< ---
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("Database connection successful.")

    # --- 3. Iterate and Update Database ---
    print("Starting database update process (this may take a few moments)...")

    for index, row in precip_df.iterrows():
        date_key_str = row['date_key'] # YYYY-MM-DD string from CSV
        time_key_str = row['time_key'] # HH:MM:SS or 24:MM:SS string from CSV
        precip_value = row['precipitation_15min_mm']

        # Determine the correct date and time range for the SQL query
        if time_key_str.startswith("24:"):
            # This represents the hour *after* 11 PM on date_key_str
            # The actual time range is on the *next* day, between 00:00:01 and 00:MM:SS

            # Calculate the next day's date string
            current_date = datetime.strptime(date_key_str, '%Y-%m-%d')
            next_day_date = current_date + timedelta(days=1)
            sql_date = next_day_date.strftime('%Y-%m-%d')

            # Convert "24:MM:SS" to "00:MM:SS" for the end time boundary
            sql_time_end = time_key_str.replace("24:", "00:", 1)

            # Calculate the start time boundary (15 mins before sql_time_end)
            # Need to handle the wrap-around carefully
            if sql_time_end == "00:00:00": # This case corresponds to 24:00:00 input
                 sql_time_start = "23:45:00" # Start is on the *previous* day logically, but we filter by next day's date
                 # We need to handle this specific interval across two days
                 # Update records for the *next* day between 00:00:00 and 00:00:00 (only exactly midnight)
                 sql_update = """
                     UPDATE logs SET precipitation = ?
                     WHERE date = ? AND time = '00:00:00' AND precipitation IS NULL;
                 """
                 params = (precip_value, sql_date) # Only need precip and the next date

                 # Also update records for the *previous* day after 23:45:00
                 sql_update_prev_day = """
                     UPDATE logs SET precipitation = ?
                     WHERE date = ? AND time > '23:45:00' AND precipitation IS NULL;
                 """
                 params_prev_day = (precip_value, date_key_str) # Use original date key

                 # Execute both updates for the midnight boundary case
                 try:
                     cursor.execute(sql_update, params)
                     cursor.execute(sql_update_prev_day, params_prev_day)
                 except sqlite3.Error as update_err:
                      print(f"Error updating for midnight boundary {date_key_str} 24:00:00: {update_err}")
                 continue # Skip the general update below for this special case

            else:
                 # For 24:15, 24:30, 24:45
                 # Calculate start time by parsing the end time and subtracting 15 mins
                 temp_end_dt = datetime.strptime(sql_time_end, '%H:%M:%S')
                 temp_start_dt = temp_end_dt - timedelta(minutes=15)
                 sql_time_start = temp_start_dt.strftime('%H:%M:%S')

        else:
            # Normal time range within the same day
            sql_date = date_key_str
            sql_time_end = time_key_str
            # Calculate start time by parsing the end time and subtracting 15 mins
            try:
                temp_end_dt = datetime.strptime(sql_time_end, '%H:%M:%S')
                temp_start_dt = temp_end_dt - timedelta(minutes=15)
                sql_time_start = temp_start_dt.strftime('%H:%M:%S')
            except ValueError:
                print(f"Skipping row due to invalid time_key format: {time_key_str}")
                continue


        # Construct the standard UPDATE statement
        sql_update = """
            UPDATE logs
            SET precipitation = ?
            WHERE
                date = ?
                AND time > ?   -- Time strictly greater than interval start
                AND time <= ?  -- Time less than or equal to interval end
                AND precipitation IS NULL;
        """
        params = (precip_value, sql_date, sql_time_start, sql_time_end)

        # Execute the update
        try:
            cursor.execute(sql_update, params)
        except sqlite3.Error as update_err:
            print(f"Error updating for interval {sql_date} {sql_time_start}-{sql_time_end}: {update_err}")
            # continue

        # Optional: Print progress periodically
        if (index + 1) % 100 == 0:
            print(f"Processed {index + 1} / {len(precip_df)} precipitation intervals...")

    # --- 4. Commit Changes and Get Total Affected Rows ---
    print("Committing changes to the database...")
    conn.commit()
    print("Database update process finished.")

    # Optional: Verify by checking remaining NULLs
    cursor.execute("SELECT COUNT(*) FROM logs WHERE precipitation IS NULL;")
    remaining_nulls = cursor.fetchone()[0]
    print(f"Number of rows still having NULL precipitation: {remaining_nulls}")


except sqlite3.Error as e:
    print(f"Database error: {e}")
    if conn:
        print("Rolling back changes due to error.")
        conn.rollback() # Rollback changes if error occurred before commit
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    if conn:
        conn.rollback()
finally:
    # --- 5. Close the Database Connection ---
    if conn:
        conn.close()
        print("Database connection closed.")

