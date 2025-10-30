library("RSQLite")
library("tidyverse")
library(correlationfunnel)
library(dplyr)

con <- dbConnect(drv=RSQLite::SQLite(), dbname="/Users/benatkinson/Library/Mobile Documents/com~apple~CloudDocs/Obsidian Vault/Projects/flatiron-flows/data/bikeLogs_eda.db")

df = dbReadTable(con,'bike_logs')

# --- 1. Load Libraries ---
library(ggplot2)
library(dplyr)
library(lubridate)

# --- 2. Load Your Data ---
# We assume your data is in a data frame named 'df'
#
# If 'date_time' is a string, convert it:
# df$date_time <- ymd_hms(df$date_time)


# --- 3. Process Data for 5-Minute Intervals ---
heatmap_data_5min <- df %>%
  mutate(
    # Extract hour and minute
    hour_of_day = hour(date_time),
    minute_of_hour = minute(date_time)
  ) %>%
  
  # --- Apply the Time Filter (9:00 AM to 5:59 PM) ---
  filter(hour_of_day >= 9, hour_of_day < 18) %>%
  
  mutate(
    # Create the 5-minute interval bin.
    # floor(minute / 5) * 5 rounds down to 0, 5, 10, ... 55
    five_min_bin = floor(minute_of_hour / 5) * 5,
    
    # Create a time label for the x-axis (e.g., "09:00", "09:05")
    # sprintf() pads with leading zeros
    time_label = sprintf("%02d:%02d", hour_of_day, five_min_bin),
    
    # Create an ordered factor for the days of the week
    day_of_week_ordered = factor(day_of_week, levels = c(
      "Monday", "Tuesday", "Wednesday", "Thursday", 
      "Friday"
    ))
  ) %>%
  
  # Group by the day and the new 5-minute time label
  group_by(day_of_week_ordered, time_label) %>%
  
  # Sum the 'pickups' for each 5-minute block
  summarise(
    total_pickups = (log(pickups) + 1),
    .groups = 'drop'
  )

# --- 4. Create the Heatmap Plot ---

# (Optional) Create a vector of breaks for the x-axis
# This will only show the label for the start of each hour
all_labels <- sort(unique(heatmap_data_5min$time_label))
hour_labels <- all_labels[seq(1, length(all_labels), by = 12)] # 12 intervals per hour

ggplot(heatmap_data_5min, aes(x = time_label, y = day_of_week_ordered, fill = total_pickups)) +
  
  geom_tile(color = "white", size = 0.1) + 
  
  scale_fill_viridis_c(name = "Total Pickups") +
  
  # Reverse the y-axis so Monday is at the top
  scale_y_discrete(limits = rev(levels(heatmap_data_5min$day_of_week_ordered))) +
  
  # --- Adjust X-axis for many labels ---
  # Use our 'hour_labels' vector to only show hourly breaks
  scale_x_discrete(breaks = hour_labels) +
  
  # Add titles and labels
  labs(
    title = "Pickup Activity by 5-Minute Interval",
    subtitle = "Filtered for 9:00 AM to 5:59 PM",
    x = "Time of Day (5-Minute Intervals)",
    y = "Day of Week"
  ) +
  
  theme_minimal() +
  
  # --- Theme adjustments to make it readable ---
  theme(
    plot.title = element_text(hjust = 0.5),
    plot.subtitle = element_text(hjust = 0.5),
    panel.grid = element_blank(),
    axis.ticks = element_blank(),
    
    # Rotate x-axis labels 90 degrees
    axis.text.x = element_text(angle = 90, vjust = 0.5, size = 8)
  )

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
  filter(hour_of_day >= 9, hour_of_day < 18) %>%
  
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

# --- 4. Create the Distribution Plot ---
# We now plot a histogram/bar chart of the 'total_pickups' column
# to see how its values are distributed.

ggplot(pickup_counts_5min, aes(x = total_pickups)) +
  
  # geom_bar() is perfect for counting discrete integer values
  geom_bar(width = 0.9, color = "white", fill = "steelblue") +
  
  # Set x-axis breaks to be integers (0, 1, 2, 3...)
  scale_x_continuous(breaks = seq(0, 20, by = 1)) +
  
  # Zoom in on the 0-10 pickup range, which is likely the
  # most common. Change or remove this as needed.
  coord_cartesian(xlim = c(-0.5, 10.5)) +
  
  labs(
    title = "Distribution of Pickups per 5-Minute Interval",
    subtitle = "Weekdays, 9:00 AM to 5:59 PM",
    x = "Total Pickups in a 5-Min Interval",
    y = "Frequency (Count of 5-Min Intervals)"
  ) +
  
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5),
    plot.subtitle = element_text(hjust = 0.5)
  )