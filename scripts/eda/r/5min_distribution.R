# --- 1. Load Required Libraries ---
library(dplyr)
library(ggplot2)
library(readr)
library(lubridate)

# --- 1.5. Load Your 5-MINUTE Data ---
# Load the CSV file
five_min_data <- read_csv("/Users/benatkinson/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/Projects/flatiron-flows/data/csv/bikeLogsAval_5min.csv")

# --- 2. Feature Engineering & Filtering ---
# Create features and filter for school days/hours
five_min_features_school <- five_min_data %>%
  mutate(
    day_of_week = wday(date_time, label = TRUE, abbr = FALSE),
    interval_5min = hour(date_time) * 12 + floor(minute(date_time) / 5),
    log_pickups = pickups_sum,
    # Create an hour column for filtering
    hour_of_day = hour(date_time) 
  ) %>%
  
  # --- KEY MODIFICATION: Filter for "School Days & Hours" ---
  filter(
    # 1. Filter for weekdays (Mon, Tue, Wed, Thu, Fri)
    !day_of_week %in% c("Saturday", "Sunday"),
    
    # 2. Filter for school hours (e.g., 8:00 AM to 7:00 PM)
    hour_of_day >= 8, hour_of_day < 19
  )

# --- 3. Generate Density Plot (School Hours) ---
print(
  ggplot(five_min_features_school, aes(x = interval_5min)) +
    geom_density(aes(weight = log_pickups), 
                 fill = "#000000", 
                 color = "#000000", 
                 alpha = 0.8,
                 bw.adjust = 0.75) + 
    
    # We now only have M-F, so ncol=5 is better, or keep ncol=3
    facet_wrap(~ day_of_week, ncol = 3) +
    
    # Set breaks for school hour intervals: 8am (96), 12pm (144), 4pm (192)
    scale_x_continuous(breaks = seq(96, 192, by = 48)) + 
    
    labs(
      title = "School Hours (M-F, 8am-5pm) Temporal Density",
      x = "5-Minute Interval of Day",
      y = "Density of Log(Pickups)"
    ) +
    theme_minimal(base_size = 14) +
    theme(legend.position = "none")
)

# --- 4. Generate QQ Plot (School Hours) ---
print(
  ggplot(five_min_features_school, aes(sample = log_pickups)) +
    geom_qq(size = 0.5) +
    geom_qq_line() +
    facet_wrap(~ day_of_week, ncol = 3, scales = "free_y") +
    labs(
      title = "School Hours (M-F, 8am-7pm) Log(Pickups) (QQ Plot)",
      x = "Theoretical Quantiles (Normal)",
      y = "Sample Quantiles (Log(Pickups))"
    ) +
    theme_minimal(base_size = 14)
)

# --- 5. Generate Histogram (School Hours) ---
print(
  ggplot(five_min_features_school, aes(x = log_pickups)) +
    geom_histogram(bins = 30, fill = "#000000", color = "white") +
    facet_wrap(~ day_of_week, ncol = 3, scales = "free_y") +
    labs(
      title = "School Hours (M-F, 8am-5pm) Log(Pickups) (Histogram)",
      x = "Log(Pickups + 1)",
      y = "Frequency (Number of Intervals)"
    ) +
    theme_minimal(base_size = 14)
)