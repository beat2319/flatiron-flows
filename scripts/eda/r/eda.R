library("RSQLite")
library("tidyverse")
library(correlationfunnel)
library(dplyr)

con <- dbConnect(drv=RSQLite::SQLite(), dbname="/Users/benatkinson/Library/Mobile Documents/com~apple~CloudDocs/Obsidian Vault/Projects/flatiron-flows/data/bikeLogs_eda.db")

df = dbReadTable(con,'bike_logs')

df %>% glimpse()

df_binary <- df %>%
  select(-index, -station_id) %>%
  mutate(TotalCharges = ifelse(is.na(TotalCharges), MonthlyCharges, TotalCharges)) %>%
  binarize(n_bins = 5, thresh_infreq = 0.01, name_infreq = "OTHER", one_hot = TRUE)