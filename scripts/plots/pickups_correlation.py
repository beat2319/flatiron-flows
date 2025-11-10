import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import sys

# --- 1. Define File Path and Plotting Style ---
CSV_PATH = '/Users/benatkinson/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/Projects/flatiron-flows/data/csv/bikeLogsAval_5min.csv'
sns.set_style("darkgrid")


def load_and_prep_data(csv_path):
    """Loads the CSV and creates all necessary features one time."""
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: File not found at {csv_path}")
        return None

    df['date_time'] = pd.to_datetime(df['date_time'])
    df = df.sort_values(by='date_time').set_index('date_time')
    
    # --- Feature Engineering ---
    df['log_pickups'] = np.log1p(df['pickups_sum'])
    df['log_min_availability'] = np.log1p(df['num_bikes_available_min'])
    df['log_mean_availability'] = np.log1p(df['num_bikes_available_mean'])
    
    df['Hour'] = df.index.hour
    df['Weekday'] = df.index.weekday # 0=Monday, 6=Sunday
    df['Weekday Name'] = df.index.day_name()
    
    df['sin_time'] = np.sin(2 * np.pi * df['Hour'] / 24)
    df['cos_time'] = np.cos(2 * np.pi * df['Hour'] / 24)
    
    # Add weather columns if they exist, handling potential errors
    df['is_precipitation'] = pd.to_numeric(df.get('is_precipitation'), errors='coerce')
    
    return df


def filter_busy_times(df):
    """Filters the DataFrame for M-F, 8am-9pm."""
    busy_hours = list(range(8, 22))  # Hours 8:00 to 21:55
    busy_days = list(range(5))       # 0 (Mon) to 4 (Fri)
    
    is_busy_hours = df['Hour'].isin(busy_hours)
    is_busy_days = df['Weekday'].isin(busy_days)
    
    return df[is_busy_hours & is_busy_days].copy()


def plot_acf_pacf(df, station_id):
    """Plots ACF and PACF for a single, specified station."""
    print(f"Plotting ACF/PACF for station: {station_id}")
    
    df_single_station = df[df['station_id'] == station_id].copy()
    if df_single_station.empty:
        print(f"Warning: Station '{station_id}' not found. Skipping ACF/PACF plot.")
        return

    print(f"Using {len(df_single_station)} 5-minute intervals.")
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    plot_acf(df_single_station['log_pickups'], lags=60, ax=axes[0])
    axes[0].set_title(f'ACF for {station_id}')

    plot_pacf(df_single_station['log_pickups'], lags=60, ax=axes[1])
    axes[1].set_title(f'PACF for {station_id}')
    
    plt.tight_layout()
    # plt.savefig('ACF_PACF.png')


def plot_activity_heatmap(df_busy):
    """Plots a heatmap of average pickups by hour and day."""
    print("Plotting activity heatmap...")
    
    heatmap_data = df_busy.groupby(['Weekday Name', 'Hour'])['log_pickups'].mean().unstack()
    
    # Order the days correctly
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    heatmap_data = heatmap_data.reindex(day_order)
    
    plt.figure(figsize=(14, 7))
    sns.heatmap(heatmap_data, cmap="viridis", annot=True, fmt=".2f")
    plt.title('Average log(Pickups) by Hour and Day (M-F, 8am-10pm)')
    # plt.savefig('pickups_heatmap.png')


def plot_correlation_matrix(df):
    """Plots a heatmap of feature correlations."""
    print("Plotting feature correlation matrix...")
    
    features_to_correlate = [
        'log_pickups', 
        'log_min_availability', 
        'sin_time', 
        'cos_time',
        'is_precipitation',
        'is_release_max'
    ]
    
    # Add other features only if they exist in the DataFrame
    if 'wind_speed_mean' in df.columns:
        features_to_correlate.append('wind_speed_mean')
    if 'temp' in df.columns:
        features_to_correlate.append('temp')
        
    # Filter out columns that don't exist
    existing_features = [col for col in features_to_correlate if col in df.columns]
    
    corr_matrix = df[existing_features].dropna().corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        corr_matrix, 
        annot=True, 
        fmt=".2f", 
        cmap="vlag",
        center=0
    )
    plt.title('Feature Correlation Matrix', fontsize=16)
    plt.tight_layout()
    plt.savefig('feature_correlation_matrix.png')


def plot_faceted_scatter(df_busy):
    """Plots the 'Wall vs. Floor' scatter plot, faceted by station."""
    print("Plotting faceted 'Wall vs. Floor' scatter plot...")
    
    g = sns.relplot(
        data=df_busy,
        x="num_bikes_available_min",
        y="pickups_sum",
        col="station_id",
        col_wrap=4,
        kind="scatter",
        alpha=0.1,
        s=5
    )

    # Add the red y=x "Wall" line to each facet
    for ax in g.axes.flat:
        lim = max(ax.get_xlim()[1], ax.get_ylim()[1])
        ax.plot([0, lim], [0, lim], ls="--", color="red")
        ax.set_xlim(0, lim)
        ax.set_ylim(0, lim)

    g.figure.suptitle("Pickups vs. Min Availability (The 'Wall vs. Floor' Plot)", y=1.03)
    # plt.savefig('faceted_wall_vs_floor.png')


def main():
    """Main function to load data and run all plotting functions."""
    
    df = load_and_prep_data(CSV_PATH)
    if df is None:
        sys.exit("Failed to load data. Exiting.")
        
    df_busy = filter_busy_times(df)
    
    # --- Generate All Plots ---
    plot_acf_pacf(df, station_id='bcycle_boulder_8889')
    plot_activity_heatmap(df_busy)
    plot_correlation_matrix(df)
    plot_faceted_scatter(df_busy)
    
    print("\nAll plots saved to disk.")
    plt.show() # Display all plots at the end

if __name__ == "__main__":
    main()