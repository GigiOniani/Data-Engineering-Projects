from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2

# Database Configuration
connection_params = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': '123456',
    'database': 'postgres'
}

# Pydantic BaseModel for request
class TransactionIDRequest(BaseModel):
    trans_id: str

# FastAPI instance
app = FastAPI()

# FastAPI GET method to retrieve total amount by trans_id
@app.get("/get_total_amount/{trans_id}")
def get_total_amount(trans_id: str):
    """
    Purpose:
    Retrieves the total amount for a given trans_id from the transactions_gold table in the PostgreSQL database.
    :param trans_id: trans_id
    :return: float amount
    """
    try:
        # Establish a PostgreSQL connection
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()

        # Fetch total amount from the database
        query = f"SELECT SUM(amount) FROM transactions_gold WHERE trans_id = '{trans_id}';"

        cursor.execute(query, (trans_id,))
        total_amount = cursor.fetchone()[0]

        if total_amount is None:
            total_amount = 0.0

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return {"trans_id": trans_id, "total_amount": total_amount}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/get_total_transactions/{cust_id}")
def number_of_transactions(cust_id: str):
    """
    Retrieves the total number of distinct transactions for a given cust_id from the transactions_gold table in the PostgreSQL database.
    :param cust_id: customer id
    :return: int of total transactions
    """
    try:
        # Establish a PostgreSQL connection
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()

        # Fetch total amount from the database
        query = f"SELECT COUNT(DISTINCT(trans_id) ) FROM transactions_gold WHERE cust_id = '{cust_id}';"

        cursor.execute(query, (cust_id,))
        total_transactions = cursor.fetchone()[0]

        if total_transactions is None:
            total_amount = 0.0

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return {"trans_id": cust_id, "total_transactions": total_transactions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data_movement_time/")
def data_movement_time():
    """
    Retrieves statistics on data movement time from the analytics table in the PostgreSQL database, including average, maximum, and minimum data delivery times.
    :return: int of average, maximum, and minimum data delivery times.
    """
    try:
        # Establish a PostgreSQL connection
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()

        # Fetch total amount from the database
        query = f"""
                    SELECT 
                      AVG(api_to_db_time) AS avg_data_delivery_time,
                      MAX(api_to_db_time) AS max_data_delivery_time,
                      MIN(api_to_db_time) AS min_data_delivery_time
                    FROM 
                      analytics;
            """

        cursor.execute(query)
        result  = cursor.fetchone()
        avg_data_delivery_time = result[0]
        max_data_delivery_time = result[1]
        min_data_delivery_time = result[2]

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return {'avg_data_delivery_time' : avg_data_delivery_time,'max_data_delivery_time' : max_data_delivery_time, 'min_data_delivery_time' :  min_data_delivery_time }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/check_rows/")
def check_rows():
    """
    Checks the total number of rows in the transactions_gold table and the number of rows logged as successfully stored in the 'app.log' file.

    :return: int
    """
    try:
        with open('app.log','r') as file:
            log_content = file.read()
        log_lines = log_content.split('\n')
        row_count = 0
        for line in log_lines:
            if "INFO:__main__:Transaction data stored successfully:" in line:
                row_count += 1

        # Establish a PostgreSQL connection
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()

        # Fetch total amount from the database
        query = f"SELECT COUNT(*) FROM transactions_gold"

        cursor.execute(query)
        total_rows = cursor.fetchone()[0]

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return {"total_rows_pg": total_rows, "logged_rows": row_count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
