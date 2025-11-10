# --- 1. Load Libraries and Data ---
library("RSQLite")
library("tidyverse")
library(lubridate) 
library(ggplot2) 

# Connect to the correct database
con <- dbConnect(drv=RSQLite::SQLite(), dbname="/Users/benatkinson/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/Projects/flatiron-flows/data/bikeLogs_hourly.db")

# Read the correct table
df_hourly <- dbReadTable(con,'hourly_bike_logs')

# Disconnect from the database
dbDisconnect(con)

# --- 2. Prepare Data for Plotting ---
hourly_pickups_filtered <- df_hourly %>%
  mutate(date_time = ymd_hms(date_time)) %>%
  mutate(hour_of_day = hour(date_time)) %>%
  filter(day_of_week %in% c(
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
  )) %>%
  mutate(day_of_week = factor(day_of_week, levels = c(
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
  ))) %>%
  filter(hour_of_day >= 8, hour_of_day < 20)

# --- 3. Aggregate data to get AVERAGE pickups ---
daily_avg_pickups <- hourly_pickups_filtered %>%
  group_by(day_of_week, station_id, hour_of_day) %>%
  summarise(
    avg_pickups = pickups_total,
    .groups = 'drop'
  )

# --- 4. Loop, Normalize, and Plot with Sin/Cos Waves ---

# Get a list of all unique station IDs
all_stations <- unique(daily_avg_pickups$station_id)

# Loop through each station ID
for (current_station in all_stations) {
  
  # 1. Filter for the current station
  station_data <- daily_avg_pickups %>%
    filter(station_id == current_station)
  
  # 2. Calculate normalization stats *across all 5 days* for this station
  min_pickups <- min(station_data$avg_pickups, na.rm = TRUE)
  max_pickups <- max(station_data$avg_pickups, na.rm = TRUE)
  range_pickups <- max_pickups - min_pickups
  
  # 3. Normalize data and add sin/cos waves
  plot_data <- station_data %>%
    mutate(
      
      # --- THIS IS THE CORRECTED LINE ---
      # Use base::ifelse() which allows for recycling arguments of different lengths
      pickups_normalized = ifelse(range_pickups == 0, 0.5, (avg_pickups - min_pickups) / range_pickups),
      # --- END CORRECTION ---
      
      # Create normalized [0, 1] sin/cos waves based on the 24-hour cycle
      sin_wave = (sin(2 * pi * hour_of_day / 24) + 1) / 2,
      cos_wave = (cos(2 * pi * hour_of_day / 24) + 1) / 2
    )
  
  # 4. Pivot data to long format for ggplot
  plot_data_long <- plot_data %>%
    pivot_longer(
      cols = c(pickups_normalized, sin_wave, cos_wave),
      names_to = "series_type",
      values_to = "value"
    ) %>%
    mutate(series_type = factor(series_type, 
                                levels = c("pickups_normalized", "sin_wave", "cos_wave"),
                                labels = c("Avg Pickups (Normalized)", "Sine Wave (24h)", "Cosine Wave (24h)")))
  
  # 5. Create the plot
  p <- ggplot(plot_data_long, 
              aes(x = hour_of_day, y = value, 
                  color = series_type, linetype = series_type, shape = series_type)) +
    
    geom_line(linewidth = 1) +
    geom_point(size = 2.5) + 
    
    facet_wrap(~ day_of_week, ncol = 1) +
    
    scale_linetype_manual(values = c("Avg Pickups (Normalized)" = "solid", 
                                     "Sine Wave (24h)" = "dashed", 
                                     "Cosine Wave (24h)" = "dotted")) +
    scale_shape_manual(values = c("Avg Pickups (Normalized)" = 16,
                                  "Sine Wave (24h)" = NA,
                                  "Cosine Wave (24h)" = NA)) +
    scale_color_manual(values = c("Avg Pickups (Normalized)" = "black", 
                                  "Sine Wave (24h)" = "blue", 
                                  "Cosine Wave (24h)" = "red")) +
    
    labs(
      title = paste("Normalized Hourly Pickups vs. Positional Encodings for Station:", current_station),
      subtitle = "Weekdays, 8:00 AM to 7:59 PM. Pickup data is Min-Max normalized [0, 1].",
      x = "Hour of the Day",
      y = "Normalized Value (0 to 1)",
      color = "Data Series",
      linetype = "Data Series",
      shape = "Data Series"
    ) +
    
    scale_x_continuous(breaks = seq(8, 20, by = 2)) +
    scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.25)) + 
    
    theme_minimal() +
    theme(
      plot.title = element_text(hjust = 0.5),
      plot.subtitle = element_text(hjust = 0.5),
      panel.spacing = unit(1, "lines"),
      legend.position = "bottom" 
    )
  
  # 6. Print the plot
  print(p)
  
  # 7. OPTIONAL: Save each plot to its own file
  file_name <- paste0("station_", current_station, "_normalized_plot.png")
  
  ggsave(
    file_name,
    plot = p,
    width = 8,
    height = 12, 
    dpi = 300
  )
}