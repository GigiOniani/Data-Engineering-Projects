from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import redis
import psycopg2
from confluent_kafka import Producer
import os
import uuid

app = FastAPI()

# Redis connection
redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=6379,
    db=1,
    decode_responses=True
)

# Kafka producer setup
producer = Producer({
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
})

KAFKA_TOPIC = "votes"

# PostgreSQL DB connection function
def get_db_connection():
    return psycopg2.connect(
        dbname='elections',
        user='postgres',
        password='postgres',
        host='postgres',
        port=5432
    )

# Request schema
class VoteRequest(BaseModel):
    personal_id: str
    guid: str
    candidate: str

@app.get("/candidates")
def get_candidates():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT leader_name, political_party FROM dim_leaders ORDER BY leader_name")
    candidates = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        {"leader_name": leader, "political_party": party}
        for leader, party in candidates
    ]

@app.post("/vote")
def cast_vote(request: VoteRequest = Body(...)):
    personal_id = request.personal_id
    guid = request.guid
    candidate = request.candidate

    # 1. Redis: Check if voter exists
    if not redis_client.exists(personal_id):
        raise HTTPException(status_code=404, detail="Voter not found")

    # 2. Redis: Fetch GUID and status
    stored_guid, status = redis_client.hmget(personal_id, "token_id", "status")

    # 3. Validate GUID
    if stored_guid != guid:
        raise HTTPException(status_code=403, detail="Invalid GUID")

    # 4. Check if already used
    if status == "used":
        raise HTTPException(status_code=403, detail="This GUID has already been used")

    # 5. PostgreSQL: Check if candidate exists
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM dim_leaders WHERE leader_name = %s", (candidate,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid candidate")
    cursor.close()
    conn.close()

    # 6. Redis: Mark token as used
    redis_client.hset(personal_id, "status", "used")

    # 7. Kafka: Send anonymized vote
    random_key = str(uuid.uuid4())
    try:
        producer.produce(KAFKA_TOPIC, key=random_key, value=candidate)
        producer.flush()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kafka error: {str(e)}")

    return {"message": "Vote submitted successfully!"}
