# --- 1. Load Required Libraries ---
# install.packages(c("dplyr", "ggplot2", "tidyr", "readr", "lubridate"))
library(dplyr)
library(ggplot2)
library(tidyr)
library(readr)
library(lubridate)

# --- 1.5. Load Your Data ---
# Load the 5-minute bike log data
bike_data <- read_csv("/Users/benatkinson/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/Projects/flatiron-flows/data/csv/bikeLogsAval_5min.csv")

ggplot(bike_data, aes(x = 1:nrow(bike_data), y = (pickups_sum))) + geom_line()