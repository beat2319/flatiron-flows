library("RSQLite")
library("tidyverse")
library(correlationfunnel)
library(dplyr)

con <- dbConnect(drv=RSQLite::SQLite(), dbname="/Users/benatkinson/Library/Mobile Documents/com~apple~CloudDocs/Obsidian Vault/Projects/flatiron-flows/data/bikeLogs_eda.db")

df = dbReadTable(con,'bike_logs')

library(ggplot2)
library(dplyr)
library(lubridate)

# --- 2. Create the 5-Minute Pickup Counts (From Your Original Code) ---
pickup_counts_5min <- df %>%
  mutate(
    hour_of_day = hour(date_time)
  ) %>%
  
  # --- Apply Filters ---
  # Filter for Weekdays (Mon-Fri)
  filter(day_of_week %in% c(
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
  )) %>%
  
  # Filter for 9:00 AM to 5:59 PM
  filter(hour_of_day >= 8, hour_of_day < 20) %>%
  
  mutate(
    # Get the date to group by specific days
    date = as.Date(date_time),
    
    # Create the 5-minute interval bin
    minute_of_hour = minute(date_time),
    five_min_bin = floor(minute_of_hour / 5) * 5
  ) %>%
  
  # Group by each unique 5-minute block
  group_by(date, hour_of_day, five_min_bin) %>%
  
  # Count the pickups in that block
  summarise(
    total_pickups = sum(pickups),
    .groups = 'drop'
  )

# --- 3. Create the NEW Log-Transformed Distribution Plot ---
# This plot will look much more "normal" and less skewed
ggplot(pickup_counts_5min, aes(x = log1p(total_pickups))) +
  
  # geom_histogram() is better for continuous-like data
  geom_histogram(bins = 20, fill = "steelblue", color = "white") +
  
  labs(
    title = "Log-Transformed Distribution of Pickups",
    subtitle = "5-Minute Intervals (Weekdays, 8am-8pm)",
    # Use log1p(x) which is log(x + 1)
    x = "Log(Total Pickups + 1)",
    y = "Frequency (Count of 5-Min Intervals)"
  ) +
  
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5),
    plot.subtitle = element_text(hjust = 0.5)
  )