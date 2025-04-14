import sqlite3 from 'sqlite3';
import dotenv from 'dotenv';
import fetch from 'node-fetch';
dotenv.config();

const db = new sqlite3.Database('./bike_logs.db');

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
    WHERE DATE(timestamp) = DATE('now', 'localtime')
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