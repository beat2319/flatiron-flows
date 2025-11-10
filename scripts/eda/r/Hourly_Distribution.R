# --- 1. Load Required Libraries ---
library(dplyr)
library(ggplot2)
library(readr)
library(lubridate)

# --- 1.5. Load Your HOURLY Data ---
hourly_data <- read_csv("/Users/benatkinson/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/Projects/flatiron-flows/data/csv/hourly_bikeLogs.csv")

# --- 2. Feature Engineering ---
hourly_features <- hourly_data %>%
  mutate(
    day_of_week = wday(date_time, label = TRUE, abbr = FALSE),
    interval_1h = hour(date_time)
  )

filter(
  # 1. Filter for weekdays (Mon, Tue, Wed, Thu, Fri)
  !day_of_week %in% c("Saturday", "Sunday"),
  
  # 2. Filter for school hours (e.g., 8:00 AM to 7:00 PM)
  hour_of_day >= 8, hour_of_day < 19
  )

# --- 3. Generate Density Plot ---
print(
  ggplot(hourly_features, aes(x = interval_1h)) +
    
    # --- MODIFICATION: Use weight = pickups_total ---
    geom_density(aes(weight = pickups_total), 
                 fill = "#000000", 
                 color = "#000000", 
                 alpha = 0.8,
                 bw.adjust = 1.0) + 
    
    facet_wrap(~ day_of_week, ncol = 3) +
    
    scale_x_continuous(breaks = seq(0, 24, by = 6)) +
    
    labs(
      x = "1-Hour Interval of Day (0-23)",
      y = "Density of Pickups"
    ) +
    
    theme_minimal(base_size = 14) +
    theme(legend.position = "none")
)

# --- 2. Feature Engineering ---
hourly_features <- hourly_data %>%
  mutate(
    day_of_week = wday(date_time, label = TRUE, abbr = FALSE)
  )

# --- 3. Generate QQ Plot (Faceted by Day) ---
print(
  ggplot(hourly_features, aes(sample = log(pickups_total+1))) +
    geom_qq(size = 0.5) +
    geom_qq_line() +
    facet_wrap(~ day_of_week, ncol = 3, scales = "free_y") +
    labs(
      title = "Hourly Pickup Distribution (QQ Plot)",
      x = "Theoretical Quantiles (Normal)",
      y = "Sample Quantiles (pickups_total)"
    ) +
    theme_minimal(base_size = 14)
)

# --- 4. Generate Histogram (Faceted by Day) ---
print(
  ggplot(hourly_features, aes(x = pickups_total)) +
    # Use a wider binwidth since hourly counts are larger
    geom_histogram(binwidth = 5, fill = "#000000", color = "white") + 
    facet_wrap(~ day_of_week, ncol = 3, scales = "free_y") +
    labs(
      title = "Hourly Pickup Distribution (Histogram)",
      x = "Total Pickups (per Hour)",
      y = "Frequency (Number of Hours)"
    ) +
    theme_minimal(base_size = 14)
)