from . import conn, replay_wal
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
import os
import psycopg2
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

import logging


scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(replay_wal, 'interval', minutes=1)
    scheduler.start()
    logging.info("Scheduler started for WAL replay")
    yield
    scheduler.shutdown()
    logging.info("Scheduler shut down")

app = FastAPI(lifespan=lifespan)

# Ensure the directory exists
os.makedirs("./logs", exist_ok=True)

LOG_FILE = os.getenv("LOG_FILE", "./logs/transactions.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)

DB_HOST = os.getenv("DB_HOST", "db")  # should be 'db' inside Docker
DB_PORT = os.getenv("DB_PORT", "5432")       # port inside container
DB_NAME = os.getenv("DB_NAME", "app_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

class User(BaseModel):
    name: str
    age: int

class Transaction(BaseModel):
    transaction_id: str
    product_id: int
    user_id: str
    dt_timestamp: datetime
    branch_id: str
    quantity: int
    unit_price: Decimal




@app.get("/")
def root():
    return {"message": "FastAPI + PostgreSQL running!"}




# @app.post("/create_production_db")
# def create():
#     try:
#         create_production_database(conn)
#         return {"message": "Table created successfully!"}
#     except Exception as e:
#         return {"status": "error", "details": str(e)}

#
# @app.post("/create_transaction_table")
# def create_transaction_table_fp():
#     try:
#         create_transaction_table(conn)
#         return {"message": "Table created successfully!"}
#     except Exception as e:
#         return {"status": "error", "details": str(e)}
#
# @app.post("/create_users_table")
# def create_users_table_fp():
#     try:
#         create_users_table(conn)
#         return {"message": "Table created successfully!"}
#     except Exception as e:
#         return {"status": "error", "details": str(e)}


@app.post("/create_transaction")
def insert_data(transaction: Transaction):
    calculated_amount = transaction.unit_price * transaction.quantity
    txn_id = transaction.transaction_id

    log_msg = (
        f"{txn_id} | PENDING | ID: {txn_id}, Product: {transaction.product_id}, "
        f"User: {transaction.user_id}, Time: {transaction.dt_timestamp}, "
        f"Branch: {transaction.branch_id}, Amount: {calculated_amount}, "
        f"Qty: {transaction.quantity}, UnitPrice: {transaction.unit_price}"
    )
    logging.info(log_msg)

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO transactions
                    (transaction_id, product_id, user_id, dt_timestamp, branch_id, amount, quantity, unit_price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        txn_id,
                        transaction.product_id,
                        transaction.user_id,
                        transaction.dt_timestamp,
                        transaction.branch_id,
                        calculated_amount,
                        transaction.quantity,
                        transaction.unit_price,
                    )
                )
            conn.commit()
            logging.info(f"{txn_id} | COMMITTED")
            print(f"{txn_id} | COMMITTED")
            return {"status": "success", "message": f"Transaction {txn_id} inserted."}

    except Exception as e:
        logging.error(f"{txn_id} | FAILED | {e}")
        print(f"{txn_id} | FAILED | {e}")
        return {"status": "error", "details": str(e)}

@app.post("/replay_wal")
def replay_wal_fp():
    try:
        replay_wal()  # execute the function
        return {"status": "success", "message": "Replay completed"}
    except Exception as e:
        logging.error(f"Replay WAL failed: {e}")
        return {"status": "error", "details": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
