import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from redis import StrictRedis
import logging
from datetime import datetime
from uvicorn import run

# Initialize the logger
logging.basicConfig(filename='app.log', level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


# Pydantic class definition
class Transaction(BaseModel):
    CUST_ID: str
    START_DATE: str
    END_DATE: str
    TRANS_ID: str
    DATE: str
    YEAR: int
    MONTH: int
    DAY: int
    EXP_TYPE: str
    AMOUNT: float

# Connect to StrictRedis
redis_client = StrictRedis(host='localhost', port=6379, decode_responses=True)

# FastAPI POST method
@app.post("/send_transaction")
async def send_transaction(transaction: Transaction):
    """
    Receives transaction data through a FastAPI POST endpoint, processes it, and stores it in Redis.
    It uses Pydantic for data validation, adds a timestamp, and logs successful transactions.
    :param transaction: Pydantic model (Transaction) representing the structure of the incoming transaction data.
    :return: data
    """
    try:
        # Convert Pydantic object to dictionary
        transaction_dict = transaction.dict()

        # Use TRANS_ID as the key in Redis
        redis_key = f"{transaction.TRANS_ID}"

        # Add timestamp to the transaction data
        transaction_dict['post_timestamp'] = datetime.utcnow().isoformat()

        # Convert values to strings before storing in Redis
        transaction_dict_str = {key: str(value) for key, value in transaction_dict.items()}

        # Store the transaction data in Redis
        redis_client.hmset(redis_key, transaction_dict_str)

        logger.info(f"Transaction data stored successfully: {transaction_dict}")

        return {"message": "Transaction data stored successfully"}

    except Exception as e:
        logger.error(f"Error while processing transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    uvicorn.run(app)
