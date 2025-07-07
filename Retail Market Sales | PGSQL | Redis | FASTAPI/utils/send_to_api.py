import pandas as pd
import requests

# Path to your CSV file
csv_file_path = 'C://Users//User//Desktop//first_100_rows.csv'

# Specify the API endpoint
api_endpoint = 'http://127.0.0.1:8000/send_transaction/'

# Function to send a single row to the API
def send_row_to_api(row_data):
    """
    Sends a single row of data to a specified API endpoint using the requests library.
    Handles exceptions, logs success, and provides error messages in case of failure.
    :param row_data: data
    :return:
    """
    try:
        response = requests.post(api_endpoint, json=row_data)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        print(row_data)
        print("Data sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send data. Error: {e}")

# Read the CSV file using pandas
try:
    df = pd.read_csv(csv_file_path)

    for _, row in df.iterrows():
        # Convert the row to a dictionary with the required keys
        row_data = {
            "CUST_ID": str(row["CUST_ID"]),
            "START_DATE": str(row["START_DATE"]),
            "END_DATE": str(row["END_DATE"]),
            "TRANS_ID": str(row["TRANS_ID"]),
            "DATE": str(row["DATE"]),
            "YEAR": int(row["YEAR"]),
            "MONTH": int(row["MONTH"]),
            "DAY": int(row["DAY"]),
            "EXP_TYPE": str(row["EXP_TYPE"]),
            "AMOUNT": float(row["AMOUNT"])
        }

        # Send each row individually to the API
        send_row_to_api(row_data)

except pd.errors.EmptyDataError:
    print("CSV file is empty.")
except FileNotFoundError:
    print("CSV file not found.")
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")