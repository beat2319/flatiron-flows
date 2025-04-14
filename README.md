## flatiron-flows ##
# CU Boulder Bike Usage Logger

This project logs bike station availability, weather, and AQI data every 15 minutes using Node.js and SQLite.

## Features
- B-cycle GBFS feed integration
- OpenWeatherMap + AQI logging
- SQLite time-series database
- Dockerized + cron-compatible
- GIS feature support (e.g. cafe proximity)

## Setup

1. Copy `.env.example` → `.env` and fill in your API key
2. Run: `docker compose up --build`
3. Add cron job to run: `docker exec bcycle_logger node log.js`

## File Overview
- `fetchData.js` — joins live data
- `db.js` — database schema and logging
- `log.js` — entry point for timed logging
- `Dockerfile` — container setup
