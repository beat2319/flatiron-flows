// This allows the env variables to be used in the code
// will have to run npm install dotenv on server
require('dotenv').config();
const OPENWEATHER_API_KEY = process.env.OPENWEATHER_API_KEY;
const LAT = process.env.LAT;
const LON = process.env.LON;

const openweather_url = `https://api.openweathermap.org/data/2.5/weather?lat=${LAT}&lon=${LON}&appid=${OPENWEATHER_API_KEY}`;
const openweather_aqi_url = `https://api.openweathermap.org/data/2.5/air_pollution?lat=${LAT}&lon=${LON}&appid=${OPENWEATHER_API_KEY}`;
const bcycle_info_url = `https://gbfs.bcycle.com/bcycle_boulder/station_information.json`;
const bcycle_status_url = `https://gbfs.bcycle.com/bcycle_boulder/station_status.json`;

fetchJoinedStationData();

// This function fetches the joined data from the Bcycle API and OpenWeather API
// and returns an array of objects containing the station information and weather data
async function fetchJoinedStationData() {
    try {
        const infoRes = await fetch(bcycle_info_url);
        const statusRes = await fetch(bcycle_status_url);
        const weatherRes = await fetch(openweather_url);
        const aqiRes = await fetch(openweather_aqi_url);
        const weatherData = await weatherRes.json();
        const aqiData = await aqiRes.json();
        
        const infoData = await infoRes.json();
        const statusData = await statusRes.json();
        const temp = weatherData.main.temp;
        const humidity = weatherData.main.humidity;
        const wind_speed = weatherData.wind.speed;
        const aqi = aqiData.list[0].main.aqi;
        const { date, time } = getDateTimeParts();
        
        const cuStationNames = new Set([
            "Folsom & Colorado",
            "18th & Colorado",
            "18th & Euclid",
            "Broadway & Euclid",
            "CU Recreation Center",
            "Macky Auditorium",
            "19th @ Boulder Creek",
            "13th & University",
            "Center for Community @ Regent Drive",
            "Farrand Field",
            "Kittredge West"
        ]);
          
        const allStations = infoData.data.stations;
        const cuStationInfo = allStations.filter(station =>
            cuStationNames.has(station.name)
        );
        
        const statusMap = new Map();
            statusData.data.stations.forEach(status => {
            statusMap.set(status.station_id, status);
        });
        
        const cuJoinedStations = cuStationInfo.map(info => {
            const status = statusMap.get(info.station_id);
            return {
              station_id: info.station_id,
              name: info.name,
              lat: info.lat,
              lon: info.lon,
              bikes_available: status?.num_bikes_available ?? null,
              docks_available: status?.num_docks_available ?? null,
              temp,
              humidity,
              wind_speed,
              aqi,
              date,
              time
            };
        });
        // console.log(cuJoinedStations);
        return cuJoinedStations;
    } 

    catch (error) {
        console.error('Error fetching Bcycle station data:', error);       
    }
}

// gives time and date with respect to 24 hours
function getDateTimeParts() {
    const now = new Date().toLocaleString('en-US', {
      timeZone: 'America/Denver',
      hour12: false,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  
    const [date, time] = now.split(', ');
    const [mm, dd, yyyy] = date.split('/');
    return {
      date: `${yyyy}-${mm}-${dd}`,
      time
    };
}

module.exports = { fetchJoinedStationData };


