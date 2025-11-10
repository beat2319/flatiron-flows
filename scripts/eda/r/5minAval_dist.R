# --- 1. Load Required Libraries ---
library(dplyr)
library(ggplot2)
library(readr)
library(lubridate)

# --- 1.5. Load Your COMBINED 5-MINUTE Data ---
# Using the relative path and new 5-minute data
csv_path <- "/Users/benatkinson/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/Projects/flatiron-flows/data/csv/bikeLogsAval_5min.csv"
combined_data <- read_csv(csv_path)

# --- 2. Feature Engineering & Filtering ---
model_data <- combined_data %>%
  mutate(
    day_of_week = wday(date_time, label = TRUE, abbr = FALSE),
    
    # Use the resampled pickup column
    log_pickups = log(pickups_sum + 1),
    
    # Use the new 'min' availability feature
    log_min_availability = log(num_bikes_available_min + 1),
    
    hour_of_day = hour(date_time) 
  ) %>%
  filter(
    !day_of_week %in% c("Saturday", "Sunday"),
    hour_of_day >= 8, hour_of_day < 19 # 8:00 AM to 6:55 PM
  )

# --- 3. Generate New Plots ---

# --- PLOT 1: How often are stations empty? ---
# This shows the size of the "stock-out" problem.
print(
  ggplot(model_data, aes(x = num_bikes_available_min)) +
    geom_histogram(binwidth = 1, fill = "#0072B2", color = "white") +
    labs(
      title = "Distribution of 5-min *Minimum* Availability (M-F, 8am-7pm)",
      x = "Minimum Bikes Available in 5-min Window",
      y = "Frequency (Number of 5-min Intervals)"
    ) +
    theme_minimal(base_size = 14)
)

# --- PLOT 2: How does availability limit pickups? ---
# This scatter plot shows the constraint.
print(
  ggplot(model_data, aes(x = num_bikes_available_min, y = pickups_sum)) +
    geom_point(alpha = 0.1, size = 0.5) + # 'alpha' helps see dense areas
    
    # This red line (y=x) shows the MAXIMUM possible pickups.
    # Points on this line are "stock-outs" where pickups = availability.
    geom_abline(intercept = 0, slope = 1, color = "red", linetype = "dashed") + 
    
    labs(
      title = "Pickups vs. Minimum Availability (M-F, 8am-7pm)",
      x = "Minimum Bikes Available in 5-min Window",
      y = "Actual Pickups (5-min Sum)"
    ) +
    theme_minimal(base_size = 14)
)

# --- PLOT 3: What is the "TRUE DEMAND" distribution? ---
# This is the histogram *excluding* all intervals that had a stock-out.
print(
  ggplot(filter(model_data, num_bikes_available_min > 0), aes(x = log_pickups)) +
    geom_histogram(bins = 30, fill = "#000000", color = "white") +
    facet_wrap(~ day_of_week, ncol = 3, scales = "free_y") +
    labs(
      title = "Histogram of 'True Demand' (When Min. Bikes Available > 0)",
      x = "Log(Pickups_Sum + 1)",
      y = "Frequency (Number of Intervals)"
    ) +
    theme_minimal(base_size = 14)
)

# --- PLOT 4: The "TRUE DEMAND" QQ Plot ---
# This will be your cleanest distribution yet.
print(
  ggplot(filter(model_data, num_bikes_available_min > 0), aes(sample = log_pickups)) +
    geom_qq(size = 0.5) +
    geom_qq_line() +
    facet_wrap(~ day_of_week, ncol = 3, scales = "free_y") +
    labs(
      title = "QQ Plot of 'True Demand' (When Min. Bikes Available > 0)",
      x = "Theoretical Quantiles (Normal)",
      y = "Sample Quantiles (Log(Pickups))"
    ) +
    theme_minimal(base_size = 14)
)