const sqlite3 = require('sqlite3').verbose();

const path = require('path');
const dbPath = path.join(__dirname,'..', 'data', 'bike_logs.db');
const db = new sqlite3.Database(dbPath);

db.serialize(() => {
    db.run(`
        CREATE TABLE IF NOT EXISTS logs (
        station_id TEXT,
        name TEXT,
        lat REAL,
        lon REAL,
        bikes_available INTEGER,
        docks_available INTEGER,
        temp REAL,
        humidity REAL,
        wind_speed REAL,
        aqi INTEGER,
        date TEXT,
        time TEXT,
        is_weekend INTEGER,
        is_semester INTEGER
        )
    `);
});

function logToDatabase(dataArray) {
    return new Promise((resolve, reject) => {
        const stmt = db.prepare(`
            INSERT INTO logs (
                station_id, name, lat, lon,
                bikes_available, docks_available,
                temp, humidity, wind_speed, aqi,
                date, time, is_weekend, is_semester
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);
  
        dataArray.forEach(row => {
            stmt.run(
                row.station_id,
                row.name,
                row.lat,
                row.lon,
                row.bikes_available,
                row.docks_available,
                row.temp,
                row.humidity,
                row.wind_speed,
                row.aqi,
                row.date,
                row.time,
                row.is_weekend ? 1 : 0, 
                row.is_semeseter ? 1 : 0 
            );
        });
  
        stmt.finalize(err => {
            if (err) reject(err);
            else resolve(`Logged ${dataArray.length} records`);
        });
    });
}

module.exports = { logToDatabase };