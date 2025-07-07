# spam_transactions.py

import requests
from faker import Faker
import random
from decimal import Decimal
from datetime import datetime
import uuid
import time

fake = Faker()

FASTAPI_URL = "http://fastapi_app:8000/create_transaction"  # internal Docker hostname

def generate_transaction():
    unit_price = Decimal(random.uniform(5.0, 50.0)).quantize(Decimal("0.01"))
    quantity = random.randint(1, 10)
    amount = (unit_price * quantity).quantize(Decimal("0.01"))

    return {
        "transaction_id": str(uuid.uuid4()),
        "product_id": random.randint(1000, 9999),
        "user_id": fake.uuid4(),
        "dt_timestamp": datetime.utcnow().isoformat(),
        "branch_id": fake.bothify(text="BR###"),
        "amount": str(amount),
        "quantity": quantity,
        "unit_price": str(unit_price)
    }

def spam_transactions(count=200, delay=0.05):
    for _ in range(count):
        txn = generate_transaction()
        try:
            response = requests.post(FASTAPI_URL, json=txn)
            print(f"Sent txn {txn['transaction_id']} → Status: {response.status_code}")
        except Exception as e:
            print(f"Failed to send: {e}")
        time.sleep(delay)

if __name__ == "__main__":
    spam_transactions(count=10000, delay=0.01)
