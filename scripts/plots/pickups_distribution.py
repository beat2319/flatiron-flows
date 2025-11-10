import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys

# Define your file path
CSV_PATH = '/Users/benatkinson/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/Projects/flatiron-flows/data/csv/bikeLogsAval_5min.csv'

# Set the seaborn theme
sns.set_theme(style="darkgrid")

def load_and_prep_data(csv_path):
    """Loads the CSV and creates all necessary features."""
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: File not found at {csv_path}")
        return None

    df['date_time'] = pd.to_datetime(df['date_time'])
    df = df.sort_values(by='date_time').set_index('date_time')

    # Add new features directly to the main DataFrame
    df['log_pickups'] = np.log1p(df['pickups_sum'])
    
    # *** THIS IS THE CORRECTED LINE ***
    df['bikes_aval_min'] = df['num_bikes_available_min']
    
    # Get time features
    df['Weekday'] = df.index.weekday
    df['Weekday Name'] = df.index.day_name()
    df['Hour'] = df.index.hour
    
    return df

def filter_busy_times(df_in):
    """
    Filters the DataFrame for busy hours (M-F, 8:00am - 9:55pm).
    """
    df = df_in.copy()
    
    # Define busy hours (8am to 9pm, inclusive)
    busy_hours = list(range(8, 22))
    # Define busy days (0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri)
    busy_days = list(range(5))

    is_busy_hours = df['Hour'].isin(busy_hours)
    is_busy_days = df['Weekday'].isin(busy_days)

    # Return only the rows that match the busy mask
    return df[is_busy_hours & is_busy_days]

def main():
    """Load, filter, and plot data."""
    
    dataset = load_and_prep_data(CSV_PATH)
    if dataset is None:
        sys.exit("Failed to load data. Exiting.")
        
    just_busy = filter_busy_times(dataset)
    
    plot_columns = ['log_pickups', 'bikes_aval_min']
    
    # --- Plot 1: Distribution by Hour ---
    print("Generating distribution_by_hour.png...")
    fig_hour, axes_hour = plt.subplots(len(plot_columns), 1, figsize=(11, 10), sharex=True)
    fig_hour.suptitle('Distribution by Hour (M-F, 8am-10pm)', fontsize=16)

    for ax, col_name in zip(axes_hour, plot_columns):
        sns.boxplot(data=just_busy, x='Hour', y=col_name, ax=ax)
        if col_name == 'log_pickups':
            ax.set_ylabel('log(Pickups + 1)')
        else:
            ax.set_ylabel('Min. Bikes Available')

    plt.xlabel('Hour of Day')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('distribution_by_hour.png')

    # --- Plot 2: Distribution by Day ---
    print("Generating distribution_by_day.png...")
    fig_day, axes_day = plt.subplots(len(plot_columns), 1, figsize=(11, 10), sharex=True)
    fig_day.suptitle('Distribution by Day of Week (M-F, 8am-10pm)', fontsize=16)
    
    # Define the correct order for the days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    for ax, col_name in zip(axes_day, plot_columns):
        sns.boxplot(data=just_busy, x='Weekday Name', y=col_name, ax=ax, order=day_order)
        if col_name == 'log_pickups':
            ax.set_ylabel('log(Pickups + 1)')
        else:
            ax.set_ylabel('Min. Bikes Available')

    plt.xlabel('Day of Week')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('distribution_by_day.png')
    
    print("All plots saved.")
    plt.show()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")