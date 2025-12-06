## Model Status
- **GOAL**: Provide real time predictions of bike share availability 
- **Current Blocker**: Forecasting (30 min +)
- **Core Problem**: The 5 min intervals are sporadic
- **Solution**: Use a more smothered dataset, and focus on pickups/drop offs as the response
- **Next Step**: Clean up visualizations for quality $R^2$ and $RMSE$
---
## Raw 5 min (1-3 time steps into the future)
- ![[Pasted image 20251125175401.png]]
- ![[Pasted image 20251125175510.png]]
- Test Accuracy Scores
	- Test $R^2$ Score: 0.9396 
	- Test $RMSE$ Score: 0.2250
- 98% percent of the time there is no change in bike availability, our goal was to have a model that understands that, but also does not drop the ball in that important 2% change
	- ```
	  Total Test Samples: 6718 
	  Samples where bikes changed (Events): 135 (2.0%) 
	  ---------------------------------------- 
	  Naive Baseline RMSE: 1.26 
	  LSTM Model RMSE: 0.87 
	  ---------------------------------------- 
	  LSTM predicts changes 30.7% better than the baseline
	  ```
- Visualization of High Accuracy Intervals 
	- ![[Pasted image 20251125180348.png]]
- Overall Model Accuracy
	- ![[Pasted image 20251125180850.png]]