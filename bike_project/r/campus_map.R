# Install leaflet if you haven't already
# install.packages("leaflet")
library(sqldf)
db_path <- "/Users/benatkinson/Library/Mobile Documents/com~apple~CloudDocs/projects/flatiron-flows/data/bike_logs.db"
data <- sqldf(paste('SELECT
    station_id,
    MIN(name) AS name, 
    MIN(lat) AS lat,         
    MIN(lon) AS lon        
FROM
    "logs"
GROUP BY
    station_id
LIMIT 11;'), dbname = db_path)
# Load the library
library(leaflet)

# --- IMPORTANT ---
# 1. Create a data frame with your station data.
#    Make sure you have columns for latitude and longitude.
#    Replace this example with YOUR actual data frame.
station_data <- data.frame(
  station_id = data$station_id,
  name = data$name,
  latitude = data$lat,      
  longitude = data$lon,
  values = c(0.2007, 0.5144, 0.2451, 0.1534, 0.1319, 0.3767, 0.3538, 0.2543, 0.1894, 0.2771, 0.1669)
  # Add any other columns you want to show in popups, e.g., capacity
)

# 2. Create the interactive map object
#    - leaflet(data = station_data): Initialize map with your data
#    - addTiles(): Add the default OpenStreetMap background map
#    - addMarkers(): Add markers using your longitude and latitude columns
#      - popup = ~name: Specifies that the 'name' column should appear in a popup when clicked
#      - label = ~station_id: Specifies that 'station_id' should appear on hover (optional)
pal <- colorFactor("magma", levels = station_data$values)
map <- leaflet() %>%
  # Add first tile
  addTiles(group="One") %>%
  # Add second tile
  addProviderTiles(providers$Esri.WorldImagery, group="Two") %>%
  # Add Layer controls
  addLayersControl(baseGroups=c("One", "Two"), 
                   options=layersControlOptions(collapsed=FALSE))%>% 
  addCircleMarkers(
    data = station_data,
    lng = ~longitude,    
    lat = ~latitude,     
    popup = ~paste("<b>Station:</b>", name, "<br>", 
                   "<b>ID:</b>", station_id),
    color = ~pal(values)
    )%>%
  addLegend(
    data = station_data,
    position = "bottomright",
    pal = pal, 
    values = ~values,
    title = "Legend",
    opacity = 1)

# 3. Display the map
#    This will typically open in the RStudio Viewer pane or your default web browser
map

# --- Optional: Save the map as an HTML file ---
# install.packages("htmlwidgets")
# library(htmlwidgets)
# saveWidget(map, file = "boulder_bcycle_map.html")