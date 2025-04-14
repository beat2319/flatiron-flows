const { fetchJoinedStationData } = require('../utils/fetchData');
const { logToDatabase } = require('../utils/db');

(async () => {
  try {
    const data = await fetchJoinedStationData();
    const msg = await logToDatabase(data);
    console.log(`Logging ${data.length} records at ${new Date().toLocaleString('en-US', { timeZone: 'America/Denver' })}`);
  } 
  catch (err) {
    console.error("Failed to log:", err);
  }
})();