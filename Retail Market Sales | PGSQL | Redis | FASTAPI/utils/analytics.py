import psycopg2
from psycopg2 import pool
from redis.exceptions import RedisError
from redis import StrictRedis
import logging
import time
from datetime import datetime  # Import the datetime module

# Configure logging
logging.basicConfig(level=logging.ERROR)  # Adjust the logging level as needed

# Create a redis_client instance
redis_client = StrictRedis(host='localhost', port=6379, decode_responses=True)

# Connection pooling for PostgreSQL
pg_connection_pool = pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=10,
    host='localhost',
    port=5432,
    user='postgres',
    password='123456',
    database='postgres'
)

def save_transaction_to_postgres(redis_client, redis_key):
    """
    Continuously retrieves transaction data from Redis and stores it in a PostgreSQL database.
     It performs necessary data transformations, checks for existing records,
      and inserts new records into the database.
    :param redis_client: redis_client
    :param redis_key: redis_key - trans_id
    :return: table
    """
    while True:
        try:
            # Retrieve the transaction data from Redis
            redis_data = redis_client.hgetall(redis_key)

            # Check if the Redis data is not empty
            if not redis_data:
                raise ValueError(f"No data found in Redis for key: {redis_key}")

            # Convert 'nan' values to None and empty strings to None
            for key, value in redis_data.items():
                if value.lower() == 'nan' or value == '':
                    redis_data[key] = None

            # Acquire a connection from the pool
            with pg_connection_pool.getconn() as postgres_connection:
                # Create a cursor to interact with the database using a context manager
                with postgres_connection.cursor() as postgres_cursor:
                    # Check if a record with the same TRANS_ID already exists
                    postgres_cursor.execute("SELECT COUNT(*) FROM analytics WHERE TRANS_ID = %s", (redis_data['TRANS_ID'],))
                    count = postgres_cursor.fetchone()[0]

                    if count == 0:
                        post_timestamp_str = redis_data.get('post_timestamp')

                        # Parse the ISO-formatted timestamp string
                        post_timestamp = datetime.fromisoformat(post_timestamp_str)

                        # The rest of your code remains unchanged
                        insert_date = datetime.utcnow()
                        time_difference = insert_date - post_timestamp
                        api_to_db_time = time_difference.total_seconds()

                        # Insert the data into PostgreSQL only if it doesn't already exist
                        postgres_cursor.execute("""
                            INSERT INTO analytics
                            (post_date,insert_date,api_to_db_time,CUST_ID, START_DATE, END_DATE, TRANS_ID, DATE, YEAR, MONTH, DAY, EXP_TYPE, AMOUNT)
                            VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            redis_data.get('post_timestamp'),
                            datetime.utcnow().isoformat(),
                            api_to_db_time,
                            redis_data.get('CUST_ID', ''),
                            redis_data.get('START_DATE', ''),
                            redis_data.get('END_DATE', None),  # Replace empty string with None
                            redis_data.get('TRANS_ID', ''),
                            redis_data.get('DATE', ''),
                            int(redis_data.get('YEAR', 0)),
                            int(redis_data.get('MONTH', 0)),
                            int(redis_data.get('DAY', 0)),
                            redis_data.get('EXP_TYPE', ''),
                            float(redis_data.get('AMOUNT', 0.0))
                        ))

            # Release the connection back to the pool
            pg_connection_pool.putconn(postgres_connection)

            return {"message": f"Transaction data for Redis key {redis_key} stored successfully in PostgreSQL"}

        except psycopg2.Error as pg_error:
            logging.error(f"PostgreSQL Error: {pg_error}")
            raise Exception("An error occurred while processing the transaction.")


        except RedisError as redis_error:
            logging.error(f"Redis Error: {redis_error}")
            raise Exception("An error occurred while retrieving data from Redis.")

        time.sleep(10)  # Adjust the sleep time as needed


# Retrieve all keys from Redis
all_keys = redis_client.keys('*')

# Save data for all keys to PostgreSQL
for redis_key in all_keys:
    try:
        result = save_transaction_to_postgres(redis_client, redis_key)
        print(result["message"])


    except Exception as e:
        print(f"Error processing Redis key {redis_key}: {str(e)}")

