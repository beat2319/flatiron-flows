 **To collect data for this project we used multiple methods including web scraping, apis, and date time**
### High Level
- Web Scraping 
	- [University of Colorado ATOC Weather Network](https://sundowner.colorado.edu/weather/atoc1/)
		- Using the website URL we scape the website for the weather table
			- Then we can parse this table for the temperature, wind speed and precipitation 
- API 
	- [api open metro](https://api.open-meteo.com/v1/forecast?latitude=40.0073&longitude=-105.2660&current=precipitation)
		- We make a [[GET]] request for Boulders weather URL
			- Then we can parse this JSON and collect the precipitation
	- [gbfs bcycle station information](https://gbfs.bcycle.com/bcycle_boulder/station_information)
		- We make a [[GET]] request for the station information URL
			- Then we can parse this JSON and pick the station_ids we we want to collect
	- [gbfs bcycle station status](https://gbfs.bcycle.com/bcycle_boulder/station_status)
		- We make a [[GET]] request for the station status URL
			- Then we can parse this JSON and pick the station_ids we we want to collect
- Date Time
	- This involves simply calling the datetime python function
		- Then recording the given datetime in UTC when the request are made
### Flowchart
- ![[ff_data_logging.svg|{width=20}]]
