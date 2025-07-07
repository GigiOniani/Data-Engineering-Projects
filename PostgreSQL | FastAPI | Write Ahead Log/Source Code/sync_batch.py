import os
import psycopg2
from psycopg2.extras import execute_batch

def clone_data():
    # Connect to production DB
    prod_conn = psycopg2.connect(
        host=os.getenv("PROD_DB_HOST"),
        port=os.getenv("PROD_DB_PORT"),
        dbname=os.getenv("PROD_DB_NAME"),
        user=os.getenv("PROD_DB_USER"),
        password=os.getenv("PROD_DB_PASSWORD"),
    )

    # Connect to clone DB
    clone_conn = psycopg2.connect(
        host=os.getenv("CLONE_DB_HOST"),
        port=os.getenv("CLONE_DB_PORT"),
        dbname=os.getenv("CLONE_DB_NAME"),
        user=os.getenv("CLONE_DB_USER"),
        password=os.getenv("CLONE_DB_PASSWORD"),
    )

    prod_cursor = prod_conn.cursor()
    clone_cursor = clone_conn.cursor()

    try:
        # Ensure table exists in clone DB
        clone_cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id VARCHAR(255) PRIMARY KEY,
                product_id INT,
                user_id VARCHAR(255),
                dt_timestamp TIMESTAMP,
                branch_id VARCHAR(255),
                amount DECIMAL(10, 2),
                quantity INT,
                unit_price DECIMAL(10, 2)
            );
        """)

        # Fetch data from production
        prod_cursor.execute("SELECT * FROM transactions;")
        rows = prod_cursor.fetchall()

        insert_query = """
            INSERT INTO transactions (
                transaction_id, product_id, user_id, dt_timestamp, branch_id, amount, quantity, unit_price
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (transaction_id) DO UPDATE SET
                product_id = EXCLUDED.product_id,
                user_id = EXCLUDED.user_id,
                dt_timestamp = EXCLUDED.dt_timestamp,
                branch_id = EXCLUDED.branch_id,
                amount = EXCLUDED.amount,
                quantity = EXCLUDED.quantity,
                unit_price = EXCLUDED.unit_price;
        """

        # Use execute_batch to run efficient batch with ON CONFLICT
        execute_batch(clone_cursor, insert_query, rows)
        clone_conn.commit()

        print(f"[SYNC] Cloned {len(rows)} rows from production to clone database.")

    except Exception as e:
        print(f"[ERROR] Clone failed during operation: {e}")
        clone_conn.rollback()

    finally:
        prod_cursor.close()
        clone_cursor.close()
        prod_conn.close()
        clone_conn.close()


if __name__ == "__main__":
    try:
        clone_data()
    except Exception as e:
        print(f"[FATAL ERROR] Clone failed: {e}")
