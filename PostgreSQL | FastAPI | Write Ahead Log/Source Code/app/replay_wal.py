import psycopg2
import re
from decimal import Decimal
import os
from datetime import datetime, timezone

LOG_FILE = os.path.join("logs", "transactions.log")

DB_HOST = os.getenv("DB_HOST", "db")  # should be 'db' inside Docker
DB_PORT = os.getenv("DB_PORT", "5432")       # port inside container
DB_NAME = os.getenv("DB_NAME", "app_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

#DB connection
def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# Parse log line to extract transaction data
def parse_transaction(log_line):
    match = re.search(
        r"ID: (?P<id>[^,]+), Product: (?P<product_id>\d+), User: (?P<user_id>[^,]+), "
        r"Time: (?P<time>[^,]+), Branch: (?P<branch_id>[^,]+), Amount: (?P<amount>[\d.]+), "
        r"Qty: (?P<qty>\d+), UnitPrice: (?P<unit_price>[\d.]+)",
        log_line
    )
    if not match:
        return None

    return {
        "transaction_id": match.group("id"),
        "product_id": int(match.group("product_id")),
        "user_id": match.group("user_id"),
        "dt_timestamp": datetime.fromisoformat(match.group("time")),
        "branch_id": match.group("branch_id"),
        "amount": Decimal(match.group("amount")),
        "quantity": int(match.group("qty")),
        "unit_price": Decimal(match.group("unit_price")),
    }

# Replay logic
def replay_wal():
    if not os.path.exists(LOG_FILE):
        print("No WAL file found.")
        return

    with open(LOG_FILE, 'r') as f:
        lines = f.readlines()

    # Only use the PENDING lines to replay — they contain the actual transaction info
    pending = {}
    committed = set()

    for line in lines:
        parts = line.strip().split(" | ")
        if len(parts) < 3:
            continue

        txn_id = parts[1].strip()  # 👈 make sure this is index 1 (txn_id position)
        status = parts[2].strip()

        if status == "PENDING":
            pending[txn_id] = line  # Save the PENDING line for replay
        elif status == "COMMITTED":
            committed.add(txn_id)

    # Only replay transactions that are PENDING and not yet COMMITTED
    for txn_id, log_line in pending.items():
        if txn_id in committed:
            continue

        print(f"Replaying transaction {txn_id}")
        txn = parse_transaction(log_line)
        if not txn:
            print(f"Could not parse transaction: {txn_id}")
            continue

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO transactions
                (transaction_id, product_id, user_id, dt_timestamp, branch_id, amount, quantity, unit_price)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                txn["transaction_id"],
                txn["product_id"],
                txn["user_id"],
                txn["dt_timestamp"],
                txn["branch_id"],
                txn["amount"],
                txn["quantity"],
                txn["unit_price"],
            ))
            conn.commit()
            cur.close()
            conn.close()

            # Log COMMITTED result
            with open(LOG_FILE, "a") as lf:
                lf.write(f"{datetime.utcnow().isoformat()} | {txn_id} | COMMITTED\n")
            print(f"{txn_id} committed.")

        except Exception as e:
            error_msg = str(e).replace("\n", " ").replace("\r", " ")[:300]
            print(f"Failed to insert {txn_id}: {error_msg}")

            # Log FAILED attempt — we still retry from the original PENDING line later
            with open(LOG_FILE, "a") as lf:
                lf.write(f"{datetime.now(timezone.utc).isoformat()} | {txn_id} | FAILED | {error_msg}\n")


# if __name__ == "__main__":
#     replay_wal()
