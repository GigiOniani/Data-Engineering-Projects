import requests
import random
import time
import psycopg2

# PostgreSQL connection config
DB_CONFIG = {
    "dbname": "elections",
    "user": "postgres",
    "password": "postgres",
    "host": "postgres",
    "port": 5432
}

# List of available candidates (leaders)
leaders = [
    "Irakli Kobakhidze", "Levan Khabeishvili", "Mamuka Khazaradze",
    "Giga Bokeria", "Irma Inashvili", "Zurab Girchi Jafaridze",
    "Giorgi Vashadze", "Shalva Natelashvili",
    "Khatuna Samnidze", "Aleko Elisashvili"
]

API_URL = "http://fastapi_app:8000/vote"

def get_voters():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT personal_id, token FROM dim_voters WHERE status != 'used';")
        result = cur.fetchall()
        cur.close()
        conn.close()
        return [{"personal_id": row[0], "guid": row[1]} for row in result]
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return []

def vote(personal_id, guid):
    payload = {
        "personal_id": str(personal_id),  # <-- Convert to string
        "guid": guid,
        "candidate": random.choice(leaders)
    }

    try:
        response = requests.post(API_URL, json=payload)
        print(f"[{response.status_code}] {response.json()} for GUID: {guid}")
    except Exception as e:
        print(f"Error voting for {guid}: {e}")

# Start spamming
voters = get_voters()

for voter in voters:
    vote(voter["personal_id"], voter["guid"])
    time.sleep(random.uniform(0.5, 1.5))  # Simulate real-time delay
