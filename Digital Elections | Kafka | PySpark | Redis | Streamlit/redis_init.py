import redis
import psycopg2
from psycopg2 import Error

def insert_data_into_redis():
    REDIS_HOST = 'redis'
    REDIS_PORT = 6379
    REDIS_DB_USER_TOKEN = 1

    # Initialize Redis client
    try:
        redis_client = redis.StrictRedis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB_USER_TOKEN,
            decode_responses=True
        )
        redis_client.ping()  # Test connection
        print("Connected to Redis successfully")
    except redis.ConnectionError as e:
        print(f"Failed to connect to Redis: {e}")
        return

    # Initialize database connection (adjust parameters as needed)
    try:
        conn = psycopg2.connect(
            dbname="elections",
            user="postgres",
            password="postgres",
            host="postgres",
            port="5432"
        )
        cursor = conn.cursor()
        print("Connected to Postgres successfully")
    except Error as e:
        print(f"Failed to connect to Postgres: {e}")
        return

    # Fetch data
    try:
        cursor.execute("SELECT personal_id, token, status FROM dim_voters")
        rows = cursor.fetchall()
        print(f"Fetched {len(rows)} rows from dim_voters")
        if not rows:
            print("No data found in dim_voters table")
            cursor.close()
            conn.close()
            return
    except Error as e:
        print(f"Error executing query: {e}")
        cursor.close()
        conn.close()
        return

    # Insert into Redis
    try:
        for row in rows:
            personal_id, token_id, status = row
            if not personal_id:
                print(f"Skipping row with empty personal_id: {row}")
                continue
            key = personal_id
            redis_client.hset(key, mapping={
                'token_id': token_id,  # key-value pair
                'status': status  # key-value pair
            })
            print(f"Inserted data for key {key}")
    except redis.RedisError as e:
        print(f"Error inserting into Redis: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    cursor.close()
    conn.close()
    print("Data insertion into Redis completed")

insert_data_into_redis()