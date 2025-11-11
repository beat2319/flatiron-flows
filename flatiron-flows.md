# Flatirons Flow ML Project
## Project Status
 - **Goal:** Forecast 5-minute bike pickup demand for CU Campus Bike share
- **Current Blocker:** Finalizing data analysis and defining model architecture 
- **Core Problem:** Data is highly zero-inflated (75% + are zeros) and non linear due to "OOS" stations and low demand
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
- **`log_pickups:`** Log transformed 5-min total pickups `(log(pickups + 1))`
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
	-  Each station has different availability and pickups, and thus demands
---
## Training Methodology 
### Data Preparation & Sequencing
- **Data Split: ** Chronological split ($80$ train / $20$ test) and  `Shuffle = False`
- **Normalization: ** `Standard Scaler` = `((data - mean)/std)` and Scaler will only fit the training data
- **Sequencing: **   Use sliding window `(create_input_output_sequences)` with `num_past_steps` = $6$ and `num_future_steps` = $1$
	- *two* input & one output
	- **`X_seq:`** `(samples 6,5)` array (6 steps, 5 features)
	- **`X_id:`** `(samples, 1)` array (`station_int_id` for each sequence)
	- **`y-target:`** `(samples, 1)` array (`log_pickups` value)
### Model Architecture 
- **Approach:** Pooled, Multi-Input Model
	- A single LSTM will be trained on all stations, using an embedding layer to learn station specific "quirks"
- **Core Model:** 2-layer LSTM stack combined with an embedding branch 
- **1: Temporal Branch** 
	- `lstm_1 = LSTM(256, return_sequences = True)(temporal_input)`
	- `norm_1 = LayerNormalization()(lstm_1)`
	- `drop_1 = Dropout(0.2)(norm_1)`
	- `lstm_2 = LSTM(128)(drop_1)`
	- `norm_2 = LayerNormalization()(lstm_2)`
	- `lstm_output = Dropout(0.2)(norm_2)`
- **2: Categorical Branch**
	- `embedding = Embedding(input_dim=13, output_dim=4)(station_id)`
	- `embedding_output = Flatten()(embeddign)`
- **Combine**
	- `combined = Concatenate()([lstm_output, embedding_output])`
- **Output Head**
	- `dense_out = Dense(16, activation='relu')(combined)`
	- `output = Dense(3)`
		- For 3 quantiles 0.05, 0.50, 0.95
- **Final Model**
	- `Model(inputs=[temporal_input, station_id_input], outputs=output`
### Loss Function & Validation
- **Loss Function and Quantile Loss**
	- using the `multi_quantile_loss` function
- **Optimizer:** 
	- `Adam(learning_rate=0.0005`
- **Validation:**
	- Use `EarlyStopping` monitoring `val_loss`
- **Training Call:**
	- The model will be trained with both inputs 
	- `model.fit(x=[X_seq_train, X_id_train], y=y_target_train`
---
## Apendix
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