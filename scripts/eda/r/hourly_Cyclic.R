# --- 1. Load Required Libraries ---
library(dplyr)
library(ggplot2)
library(tidyr)
library(readr)
library(lubridate)

# --- 1.5. Load Your HOURLY Data ---
# Load the CSV file
hourly_data <- read_csv("/Users/benatkinson/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/Projects/flatiron-flows/data/csv/hourly_bikeLogs.csv")

# Define the period for a full day in hours
period_hourly <- 24 # 24 hours in a day

# --- 2. Feature Engineering ---
# Create day_of_week and interval_1h from your 'datetime' column
hourly_features <- hourly_data %>%
  mutate(
    day_of_week = wday(date_time, label = TRUE, abbr = FALSE),
    interval_1h = hour(date_time)
  )

# --- 3. Scale and Add Time Features ---
hourly_comparison <- hourly_features %>%
  group_by(day_of_week) %>% 
  mutate(
    # --- MODIFICATION ---
    # Use your 'pickups' column for scaling
    scaled_count = (pickups_total - min(pickups_total)) / (max(pickups_total) - min(pickups_total)),
    
    # Handle potential "divide by zero" if min == max
    scaled_count = if_else(is.nan(scaled_count), 0, scaled_count),
    
    # Create Sin/Cos features
    time_sin_raw = sin(2 * pi * interval_1h / period_hourly),
    time_cos_raw = cos(2 * pi * interval_1h / period_hourly),
    scaled_sin = (time_sin_raw + 1) / 2,
    scaled_cos = (time_cos_raw + 1) / 2
  ) %>%
  ungroup()

# --- 4. Prepare Data for Plotting ---
hourly_plot_data <- hourly_comparison %>%
  select(day_of_week, interval_1h, `Pickups` = scaled_count, `Sin` = scaled_sin, `Cos` = scaled_cos) %>%
  distinct() %>% 
  pivot_longer(
    cols = -c(day_of_week, interval_1h),
    names_to = "metric_type",
    values_to = "value"
  )

# --- 5. Generate Plot ---
print(
  ggplot(hourly_plot_data, aes(x = interval_1h, y = value, color = metric_type)) +
    geom_line(aes(linetype = metric_type), size = 1.0, alpha = 0.9) +
    facet_wrap(~ day_of_week, ncol = 3) +
    scale_x_continuous(breaks = seq(0, 24, by = 6)) +
    labs(
      x = "1-Hour Interval of Day (0-23)",
      y = "Scaled Value (0 to 1)",
      color = "Metric",
      linetype = "Metric"
    ) +
    scale_linetype_manual(values = c("Pickups" = "solid", "Sin" = "dashed", "Cos" = "dotted")) +
    scale_color_manual(values = c("Pickups" = "#000000", "Sin" = "#0072B2", "Cos" = "#D55E00")) +
    theme_minimal(base_size = 14) +
    theme(legend.position = "bottom")
)