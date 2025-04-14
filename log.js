const { fetchJoinedStationData } = require('./fetchData');
const { logToDatabase } = require('./db');

(async () => {
  try {
    const data = await fetchJoinedStationData();
    const msg = await logToDatabase(data);
    console.log(msg);
  } catch (err) {
    console.error("Failed to log:", err);
  }
})();