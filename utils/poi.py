import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


# Sample data based on your example
station_data = [
	['bcycle_boulder_1855', 'Folsom & Colorado', 40.00811, -105.2639],
	['bcycle_boulder_1872', '19th @ Boulder Creek', 40.01167, -105.2702],
	['bcycle_boulder_2132', 'CU Recreation Center', 40.00983, -105.2703],
	['bcycle_boulder_2144', 'Broadway & Euclid', 40.00638, -105.2724],
	['bcycle_boulder_2767', '18th & Colorado', 40.00813, -105.2691],
	['bcycle_boulder_3318', '18th & Euclid', 40.00584, -105.2698],
	['bcycle_boulder_3894', 'Center for Community @ Regent Drive', 40.00426, -105.2639],
	['bcycle_boulder_4657', 'Farrand Field', 40.00660, -105.2672],
	['bcycle_boulder_7314', '13th & University', 40.01068, -105.2759],
	['bcycle_boulder_7393', 'Macky Auditorium', 40.00938, -105.2727],
	['bcycle_boulder_7785', 'Kittredge West', 40.00243, -105.2645]
]

columns = ['station_id', 'name', 'latitude', 'longitude']

stations_df = pd.DataFrame(station_data, columns=columns) 

geometry = [Point(xy) for xy in zip(stations_df['longitude'], stations_df['latitude'])]

stations_gdf = gpd.GeoDataFrame(stations_df, geometry=geometry, crs='EPSG:4326')

import osmnx as ox
import geopandas as gpd 

# --- Step 1: Get POI Data ---
place_name = "University of Colorado Boulder" 

tags_cafe = {'amenity': 'cafe'}
print(f"\nDownloading Cafes in {place_name}...")
try:
    pois_cafe_gdf = ox.features_from_place(place_name, tags_cafe)
    print(f"Downloaded {len(pois_cafe_gdf)} potential cafes.")
    # Add a column to identify POI type
    pois_cafe_gdf['poi_type'] = 'cafe'
except Exception as e:
    print(f"Could not download cafes: {e}")
    pois_cafe_gdf = gpd.GeoDataFrame() # Create empty GDF if download fails

# Example: Get Dorms
tags_dorm = {'building': 'dormitory'}
print(f"\nDownloading Dormitories in {place_name}...")
try:
    pois_dorm_gdf = ox.features_from_place(place_name, tags_dorm)
    print(f"Downloaded {len(pois_dorm_gdf)} potential dormitories.")
    pois_dorm_gdf['poi_type'] = 'dormitory'
except Exception as e:
    print(f"Could not download dormitories: {e}")
    pois_dorm_gdf = gpd.GeoDataFrame()

# Example: Get Recreation/Fields
tags_rec = {'leisure': ['park', 'pitch', 'sports_centre', 'stadium', 'recreation_ground']}
print(f"\nDownloading Recreation Areas in {place_name}...")
try:
    pois_rec_gdf = ox.features_from_place(place_name, tags_rec)
    print(f"Downloaded {len(pois_rec_gdf)} potential recreation areas.")
    pois_rec_gdf['poi_type'] = 'recreation'
except Exception as e:
    print(f"Could not download recreation areas: {e}")
    pois_rec_gdf = gpd.GeoDataFrame()

# Combine the different POI types into one GeoDataFrame
pois_gdf = pd.concat([pois_cafe_gdf, pois_dorm_gdf, pois_rec_gdf], ignore_index=True)

# Optional: Filter out non-point geometries if needed, though buffering works with polygons too
# pois_gdf = pois_gdf[pois_gdf.geometry.type == 'Point']

# Ensure the resulting GeoDataFrame has a geometry column and CRS
if 'geometry' not in pois_gdf.columns or pois_gdf.empty:
     print("Error: No POI geometries found or downloaded.")
     # Handle error appropriately - maybe exit or use default zero counts
else:
    print(f"\nTotal POIs combined: {len(pois_gdf)}")
    print("Sample POI Data:")
    print(pois_gdf[['name', 'poi_type', 'geometry']].head())
    print(f"POI CRS: {pois_gdf.crs}")

# (Your existing code to create stations_gdf and pois_gdf goes here)

# --- Step 2: Project to a suitable CRS for distance calculations ---

# Check if POIs were actually loaded before proceeding
if 'geometry' in pois_gdf.columns and not pois_gdf.empty:
    target_crs = 'EPSG:32613' # UTM Zone 13N is suitable for Boulder

    print(f"\nProjecting stations to {target_crs}...")
    stations_gdf_proj = stations_gdf.to_crs(target_crs)
    print(f"Stations projected. New CRS: {stations_gdf_proj.crs}")
    # print(stations_gdf_proj.head()) # Optional: view projected coordinates

    print(f"\nProjecting POIs to {target_crs}...")
    pois_gdf_proj = pois_gdf.to_crs(target_crs)
    print(f"POIs projected. New CRS: {pois_gdf_proj.crs}")
    # print(pois_gdf_proj.head()) # Optional: view projected coordinates

    # ----- NEXT STEPS after projection will use stations_gdf_proj and pois_gdf_proj -----
    # 3. Buffering
    # 4. Spatial Join
    # 5. Aggregation

else:
    print("\nNo POIs were loaded or geometry column missing. Cannot proceed with projection and spatial analysis.")
    # You might want to handle this case, e.g., by setting POI counts to zero later on.

# (Your existing code up to the projection step goes here)
# You should have stations_gdf_proj and pois_gdf_proj defined

# --- Step 3: Create Buffers around Stations ---
buffer_radius_meters = 250 # Define the radius for "nearby" (e.g., 250 meters)

print(f"\nCreating {buffer_radius_meters}m buffers around projected stations...")

# Create buffer polygons directly from the projected station geometries
# The distance unit (250) is interpreted in the units of the CRS (meters for EPSG:32613)
station_buffers = stations_gdf_proj.geometry.buffer(buffer_radius_meters)
print("Buffers created.")

# Create a new GeoDataFrame containing these buffer polygons
# It inherits the CRS from stations_gdf_proj
station_buffers_gdf = gpd.GeoDataFrame(geometry=station_buffers, crs=stations_gdf_proj.crs)

# Add the station_id to this new GeoDataFrame. This is crucial for linking POIs back
# to the correct station after the spatial join.
station_buffers_gdf['station_id'] = stations_gdf_proj['station_id'].values # Use .values to align correctly

print("\nSample Buffer GeoDataFrame:")
print(station_buffers_gdf.head())

# Optional: You could plot this to visualize (requires matplotlib)
# import matplotlib.pyplot as plt
# fig, ax = plt.subplots(figsize=(10, 10))
# station_buffers_gdf.plot(ax=ax, facecolor='none', edgecolor='red', label=f'{buffer_radius_meters}m Buffer')
# stations_gdf_proj.plot(ax=ax, color='blue', markersize=5, label='Stations')
# pois_gdf_proj.plot(ax=ax, color='green', markersize=2, label='POIs')
# ax.set_title('Stations, POIs, and Buffers (Projected)')
# ax.set_xlabel("Easting (meters)")
# ax.set_ylabel("Northing (meters)")
# plt.legend()
# plt.show()

# --- Step 4: Spatial Join to Count POIs within Buffers ---
# (Your existing code up to creating station_buffers_gdf goes here)
# Make sure pois_gdf_proj is also available

# --- Step 4: Spatial Join ---
# Ensure POIs were loaded before attempting join
if 'geometry' in pois_gdf_proj.columns and not pois_gdf_proj.empty:
    print("\nPerforming spatial join (finding POIs within station buffers)...")

    # Perform the spatial join: Find POIs that are 'within' station buffers
    # pois_gdf_proj is the 'left' dataframe (the points we're checking)
    # station_buffers_gdf is the 'right' dataframe (the areas we're checking against)
    pois_within_buffers_gdf = gpd.sjoin(
        pois_gdf_proj,          # GeoDataFrame of POIs
        station_buffers_gdf,    # GeoDataFrame of Station Buffers (with station_id)
        how='inner',            # 'inner' keeps only matches (POIs inside at least one buffer)
        predicate='within'      # The spatial relationship check
    )

    print(f"Join complete. Found {len(pois_within_buffers_gdf)} POI instances within various station buffers.")

    # Inspect the result of the join.
    # Note: It includes columns from BOTH input GeoDataFrames.
    # Most importantly, it now has the 'station_id' associated with the POI based on the buffer it fell into.
    # A POI might appear multiple times if it falls within more than one station's buffer.
    print("\nSample result of spatial join (POIs within buffers):")
    # Show relevant columns: POI name, POI type, and the ID of the station buffer it's within
    print(pois_within_buffers_gdf[['name', 'poi_type', 'station_id']].head(10)) # Show a few more rows

    # You can check counts per station now, though the next step aggregates this formally
    # print("\nCounts per station_id from joined data:")
    # print(pois_within_buffers_gdf['station_id'].value_counts())

else:
    print("\nSkipping spatial join as no POIs were loaded.")
    # Create an empty dataframe to avoid errors later, ensuring 'station_id' and 'poi_type' columns exist
    pois_within_buffers_gdf = pd.DataFrame(columns=['station_id', 'poi_type']) # Use pandas here

# (Your existing code up to creating pois_within_buffers_gdf goes here)

# --- Step 5: Aggregate Results ---
print("\nAggregating results (counting POIs per station per type)...")

# Check if the spatial join actually found any POIs within buffers
if not pois_within_buffers_gdf.empty:
    # Group by the station ID (from the buffer) and the type of the POI
    # .size() counts the number of rows in each group
    poi_counts = pois_within_buffers_gdf.groupby(['station_id', 'poi_type']).size()

    # Reshape the data:
    # - .unstack() moves the inner index level ('poi_type') to become column headers.
    # - fill_value=0 ensures that if a station had no POIs of a certain type, it gets a 0 count instead of NaN.
    poi_counts_df = poi_counts.unstack(fill_value=0)

    print("\nRaw POI counts per station (only stations with >0 POIs found):")
    print(poi_counts_df)

    # --- Merge with original stations list to include stations with ZERO nearby POIs ---
    print("\nMerging counts with all stations list to include zeros...")

    # Get the original list of station IDs to ensure all are represented
    all_stations = stations_gdf[['station_id']].copy()

    # Perform a left merge: Keep all rows from 'all_stations', add matching counts from 'poi_counts_df'
    final_poi_counts = pd.merge(
        all_stations,    # Left DataFrame (all station IDs)
        poi_counts_df,   # Right DataFrame (counts for stations with POIs)
        on='station_id', # Column to merge on
        how='left'       # Keep all stations from the left DataFrame
    )

    # After the merge, stations that had no POIs found will have NaN values in the count columns.
    # Fill these NaNs with 0.
    final_poi_counts = final_poi_counts.fillna(0)

    # Optional: Convert the count columns to integer type for cleanliness
    # Identify count columns (all columns except 'station_id')
    count_columns = final_poi_counts.columns.drop('station_id')
    final_poi_counts[count_columns] = final_poi_counts[count_columns].astype(int)

    print("\n--- FINAL POI Counts per Station ---")
    print(final_poi_counts)

else:
    # Handle the case where the spatial join was empty (no POIs found in any buffer)
    print("\nNo POIs were found within any station buffers during the spatial join.")
    print("Creating final counts DataFrame with all zeros.")

    # Create a DataFrame with all station IDs and zero counts for the expected POI types
    all_stations = stations_gdf[['station_id']].copy()
    # Use the types you actually queried earlier
    expected_poi_types = ['cafe', 'dormitory', 'recreation']
    for poi_type in expected_poi_types:
         all_stations[poi_type] = 0 # Add columns with zeros
    final_poi_counts = all_stations

    print("\n--- FINAL POI Counts per Station (All Zeros) ---")
    print(final_poi_counts)
