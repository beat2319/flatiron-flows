# Flatirons Flow ML Project
## Project Status
 - **Goal:** Forecast 5-minute bike pickup demand for CU Campus Bike share
- **Current Blocker:** Finalizing data analysis and defining model architecture 
- **Core Problem:** Data is highly zero-inflated (75% + are zeros) and non linear due to "OOS" stations 
- **Solution:** Feature Engineering `(log_min_availability)` as a context feature and a LSTM with an Embedding layer to handle station specific quirks 
- **Next Step:** Implement the data pipeline to create sequences and train the baseline LSTM model
---
## Data
### Definition
- **Study Area:** 13 B-Cycle Stations on CU Campus
- **Temporal Resolution:** 5-minute intervals (resampled from 1 min raw data)
- **Lookback:** 6 steps (30 min), based on [[ACF_PACF.png|PACF]] analysis
- **Total Dataset:** ~30,000 5-min intervals (2,300 per station)
## Source
[[Data Logging]]
### Response 
- **`log_pickups:`** Log transformed 5-min total pickups `(log(pickups_sum +1))`
### Predictor
- **`log_min_availability:`**  `(log(num_bikes_available_min + 1))`  identify 'OOS'
- **`sin_time/cos_time:`** Cyclical features to encode time
- **`station_id:`** A categorical feature (0-12) used as embedding layer
- **`is_release:`** Binary flag for release times
## Visualization
- **Time Series**
	- ![[pickup_trends.png]]
	- Cyclic nature of pickups
- **Heatmap**
	- ![[pickups_heatmap.png]]
	- Cyclic nature of pickups within school day
- **ACF & PACF**
	- ![[ACF_PACF.png]]
	- The PACF shows a lookback of around 6 will explain the sequence 
	- The ACF shows our pickups have strong memory 
- **Distribution of Pickups and Bikes Available** w/ grouped 5 min intervals 
	- ![[distribution_by_day.png]]
	- ![[distribution_by_hour.png]]
- **Feature Correlation** 
	- ![[feature_correlation_matrix.png]]
	- Justifies time encoding, and is_release, everything else is trivial without more data
- **Availability vs Pickups Plot**
	- ![[faceted_wall_vs_floor.png]]
	-  Each station has different availability and pickups, thus demands

##
## Model Architecture 
- Plot pickups by station
	- this will determine LSTM vs RF
- LSTM
	- Focused on sequences around the school day
		- Tune around the is_release
	- Sin Cos encoding 
		- **hours** not min
		- morning, noon, evening
-  Model for each station 
## Response 
- Pickups
## Predictor
- is_precipitaiton
- is_release
- is_holiday

## LOSS
Quantile Loss
classes based on quantiles 

## Update Terminology
- Not sample and truth
	- test and train
- Use gpt to clean up wording
## Recommendations
- don't worry about zeros
	- focus on hours 
	- 
quantile transformer
zero and non zero 
- will or wont be a pickup
- focal loss
- boulder pretraining
focus on demand hours
- have a model that comes up with demand
- these are the high demand hours and get to the target
	- feature engeiring to get to that demand point 
- One or Zero
	- if one then regression
	- location ebeddings too?
-
## Non Important Zeros
- ![[CleanShot 2025-11-09 at 14.28.37@2x.png]]
	- Using this knowledge we will only include hours (8-21)
- ![[CleanShot 2025-11-09 at 14.30.57@2x.png]]
	- Using this knowledge we will only use days (0-4)