const path = require('path');
const sqlite3 = require('sqlite3');
const dotenv = require('dotenv');
dotenv.config({ path: path.join(__dirname, '..', '.env') });

//isues with sending webhook
const fetch = (...args) => import('node-fetch').then(({ default: fetch }) => fetch(...args)); 

const db = new sqlite3.Database(path.join(__dirname, '..', 'data', 'bike_logs.db'));

function sendDiscord(message) {
  return fetch(process.env.DISCORD_WEBHOOK, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content: message }),
  });
}

function runSummary() {
  const today = new Date().toISOString().split('T')[0];

  const sql = `
    SELECT COUNT(*) AS logs, 
           ROUND(AVG(bikes_available), 1) AS avg_bikes, 
           ROUND(AVG(temp), 1) AS avg_temp,
           ROUND(AVG(wind_speed), 1) AS avg_wind,
           ROUND(AVG(aqi), 1) AS avg_aqi
    FROM logs
    WHERE date = DATE('now', 'localtime')
  `;

  db.get(sql, async (err, row) => {
    if (err) {
      console.error("Summary error:", err);
      await sendDiscord(`❌ Failed to generate daily summary: ${err.message}`);
      return;
    }

    const todayDate = new Date().toLocaleDateString("en-US", {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    });

    const message = `🗓️ **Daily Bike Log Summary (${todayDate})**\n` +
                    `🚲 **Logs today**: ${row.logs}\n` +
                    `📈 **Avg bikes**: ${row.avg_bikes}\n` +
                    `🌡️ **Avg temp**: ${row.avg_temp}K\n` +
                    `💨 **Avg wind**: ${row.avg_wind} m/s\n` +
                    `🏭 **Avg AQI**: ${row.avg_aqi}`;

    await sendDiscord(message);
    db.close();
  });
}

runSummary();