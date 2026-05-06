import time
import requests
import random
import sys
from datetime import datetime, timedelta
import sqlite3

API_URL = "http://localhost:8000/api/v1/vitals/"

def get_base_vitals():
    return {
        "heart_rate": 70,
        "spo2": 98,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80
    }

def prepopulate_db(minutes=50):
    # This directly inserts into the local SQLite DB to give the UI some history to show immediately.
    print(f"Pre-populating {minutes} minutes of history...")
    conn = sqlite3.connect('icu_vitals.db')
    c = conn.cursor()
    # Ensure table exists
    c.execute('''CREATE TABLE IF NOT EXISTS patient_vitals 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME, heart_rate FLOAT, spo2 FLOAT, 
                  blood_pressure_systolic INTEGER, blood_pressure_diastolic INTEGER, alert_level VARCHAR, ai_summary VARCHAR)''')
    
    now = datetime.now()
    records = []
    trend = 0
    base_hr = 70
    
    for i in range(minutes * 12): # approx 1 data point every 5 seconds
        t = now - timedelta(minutes=minutes) + timedelta(seconds=i*5)
        
        # Determine values with slight randomness
        chance = random.random()
        if chance < 0.02: # 2% chance of critical drop
            hr = random.randint(120, 140)
            spo2 = random.randint(85, 89)
            al = "CRITICAL"
            sumy = "Critical! High heart rate with severe hypoxemia."
        elif chance < 0.05: # 5% chance of warning
            hr = random.randint(100, 115)
            spo2 = random.randint(90, 94)
            al = "WARNING"
            sumy = "Warning: Tachycardia - patient may be stressed."
        else: # Normal drift
            trend += random.choice([-1, 0, 1])
            if trend > 5: trend -= 1
            if trend < -5: trend += 1
            hr = max(40, min(150, base_hr + trend + random.randint(-2, 2)))
            spo2 = max(80, min(100, 98 + random.randint(-1, 0)))
            al = "INFO"
            sumy = "Vitals stable."
        
        bp_s = 120 + random.randint(-5, 5)
        bp_d = 80 + random.randint(-5, 5)
        
        records.append((t.strftime('%Y-%m-%d %H:%M:%S.%f'), hr, spo2, bp_s, bp_d, al, sumy))
        
    c.executemany('INSERT INTO patient_vitals (timestamp, heart_rate, spo2, blood_pressure_systolic, blood_pressure_diastolic, alert_level, ai_summary) VALUES (?,?,?,?,?,?,?)', records)
    conn.commit()
    conn.close()
    print("Pre-population complete.")

def simulate():
    print("Starting real-time vitals drop...")
    base_hr = 70
    base_spo2 = 98
    base_bps = 120
    base_bpd = 80
    trend = 0
    
    while True:
        chance = random.random()
        if chance < 0.05:
            hr = random.randint(120, 140)
            spo2 = random.randint(85, 89)
        elif chance < 0.15:
            hr = random.randint(100, 115)
            spo2 = random.randint(90, 94)
        else:
            trend += random.choice([-1, 0, 1])
            if trend > 5: trend -= 1
            if trend < -5: trend += 1
            hr = max(40, min(150, base_hr + trend + random.randint(-2, 2)))
            spo2 = max(80, min(100, base_spo2 + random.randint(-1, 0)))
        
        bps = base_bps + random.randint(-5, 5)
        bpd = base_bpd + random.randint(-5, 5)
        
        payload = {
            "heart_rate": hr,
            "spo2": spo2,
            "blood_pressure_systolic": bps,
            "blood_pressure_diastolic": bpd
        }
        
        try:
            requests.post(API_URL, json=payload)
            print(f"Sent: {payload}")
        except Exception as e:
            print(f"Failed to connect to API: {e}")
            
        time.sleep(random.uniform(2.0, 5.0))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--prepopulate":
        prepopulate_db(60)
    simulate()
