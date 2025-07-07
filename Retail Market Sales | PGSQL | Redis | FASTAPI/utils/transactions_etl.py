import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import time
import csv
# PostgreSQL connection parameters
connection_params = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': '123456',
    'database': 'postgres'
}

# CSV file path
csv_file_path = 'C://Users//User//Desktop//transactions.csv'

# PostgreSQL table creation query
create_table_query = '''
    CREATE TABLE IF NOT EXISTS transactions_bronze (  
        CUST_ID VARCHAR(255),
        START_DATE DATE,
        END_DATE DATE,
        TRANS_ID VARCHAR(255),
        DATE DATE,
        YEAR INT,
        MONTH INT,
        DAY INT,
        EXP_TYPE VARCHAR(255),
        AMOUNT NUMERIC
    );
'''

# PostgreSQL INSERT query with NULL handling
insert_query = '''
    INSERT INTO transactions_bronze (CUST_ID, START_DATE, END_DATE, TRANS_ID, DATE, YEAR, MONTH, DAY, EXP_TYPE, AMOUNT)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
'''


def create_table():
    """
        Purpose: Creates a table in the PostgreSQL database if it doesn't already exist.

    :return: Table
    """
    try:
        # Connect to PostgreSQL
        connection = psycopg2.connect(**connection_params)
        cursor = connection.cursor()

        # Create table
        cursor.execute(create_table_query)

        # Commit changes and close connection
        connection.commit()
        cursor.close()
        connection.close()
        print("Table created successfully.")

    except Exception as e:
        print(f"Error creating table: {e}")

def insert_data_in_chunks(csv_file_path, connection_params, chunk_size=100000):
    """
 I      inserts data from a CSV file into the "transactions_bronze" table in chunks, handling NULL values.
    :param csv_file_path: Reads data from the CSV file in chunks.

    :param connection_params: connection to the PostgreSQL database
    :param chunk_size: chunksize
    :return: Inserts data into the "transactions_bronze" table in chunks with a specified size.

    """
    try:
        # Connect to PostgreSQL
        connection = psycopg2.connect(**connection_params)
        cursor = connection.cursor()

        # Read CSV file in chunks
        with open(csv_file_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            # Insert data in chunks with NULL handling
            chunk = []
            row_counter = 0  # Counter for tracking the number of rows processed

            for row in csv_reader:
                # Convert empty strings to None for NULL values
                row = {key: None if value == '' else value for key, value in row.items()}
                chunk.append(list(row.values()))
                row_counter += 1

                if row_counter == chunk_size:
                    cursor.executemany(insert_query, chunk)
                    connection.commit()
                    break  # Break out of the loop after processing the first 100,000 rows

            # Insert any remaining records
            if chunk:
                cursor.executemany(insert_query, chunk)
                connection.commit()

        # Close connection
        cursor.close()
        connection.close()
        print(f"Top {chunk_size} rows successfully inserted.")

    except Exception as e:
        print(f"Error inserting data: {e}")


def create_silver(connection_params, table_name,destination_table):
    """
    Transforms data from the "transactions_bronze" table and creates a new "silver" table with additional columns.
    :param connection_params:Establishes a connection to the PostgreSQL database
    :param table_name: transactions_bronze
    :param destination_table: transactions_silver
    :return: Writes the transformed DataFrame back to a new table named "transactions_silver" in PostgreSQL.
    """
    try:
        # Connect to PostgreSQL and read data into a DataFrame
        connection = psycopg2.connect(**connection_params)
        engine = create_engine(
            f'postgresql://{connection_params["user"]}:{connection_params["password"]}@{connection_params["host"]}:{connection_params["port"]}/{connection_params["database"]}')

        query = f'SELECT * FROM {table_name}'
        df = pd.read_sql(query, con=engine)
        df2 = df.copy()
        # Create a mapping of unique EXP_TYPE values to unique IDs
        exp_type_mapping = {exp_type: idx for idx, exp_type in enumerate(df['exp_type'].unique())}

        # Map the EXP_TYPE to its corresponding unique ID
        df['exp_id'] = df['exp_type'].map(exp_type_mapping)
        # Drop the original EXP_TYPE column if you don't need it anymore

        # Write the transformed data back to the transactions table
        df.to_sql(destination_table, con=engine, if_exists='replace', index=False)
        print('silver_created')
        # Close the PostgreSQL connection
        connection.close()

    except Exception as e:
        print(f"Error inserting data: {e}")

        # Example usage




def create_gold(connection_params, table_name,destination_table):
    """
    Transforms data from the "transactions_silver" table and creates a new "gold" table with specific columns.

    :param connection_params: Establishes a connection to the PostgreSQL database
    :param table_name: Reads data from the "transactions_silver" table into a Pandas DataFrame.
    :param destination_table: Writes the transformed DataFrame back to a new table named "transactions_gold" in PostgreSQL.

    :return: table
    """
    try:
        # Connect to PostgreSQL and read data into a DataFrame
        connection = psycopg2.connect(**connection_params)
        engine = create_engine(
            f'postgresql://{connection_params["user"]}:{connection_params["password"]}@{connection_params["host"]}:{connection_params["port"]}/{connection_params["database"]}')

        query = f'SELECT * FROM {table_name}'
        df = pd.read_sql(query, con=engine)
        # Drop the original EXP_TYPE column if you don't need it anymore
        df = df.drop(columns=['exp_type', 'start_date', 'end_date','year','day','month'])
        # Write the transformed data back to the transactions table
        df.to_sql(destination_table, con=engine, if_exists='replace', index=False)
        print('gold_created')
        # Close the PostgreSQL connection
        connection.close()
    except Exception as e:
        print(f"Error inserting data: {e}")


def etl_create_dim_customer(connection_params, transactions_table, dim_customer_table):
    """
     Creates a dimension table for customer information.

    :param connection_params: Establishes a connection to the PostgreSQL database
    :param transactions_table: Retrieves distinct CUST_ID, START_DATE, and END_DATE values from the "transactions_silver" table.
    :param dim_customer_table: Writes the retrieved data to a new table named "dim_customer_info" in PostgreSQL.

    :return: dim_customer_table
    """
    try:
        # Connect to PostgreSQL and read data into a DataFrame
        connection = psycopg2.connect(**connection_params)
        engine = create_engine(
            f'postgresql://{connection_params["user"]}:{connection_params["password"]}@{connection_params["host"]}:{connection_params["port"]}/{connection_params["database"]}')

        # Retrieve necessary columns from transactions table
        query = f'SELECT DISTINCT CUST_ID, START_DATE, END_DATE FROM {transactions_table}'
        df = pd.read_sql(query, con=engine)

        # Write the retrieved data to the dim_customer_info table
        df.to_sql(dim_customer_table, con=engine, if_exists='replace', index=False)
        print('dim_customer_created')
        # Close the PostgreSQL connection
        connection.close()

    except Exception as e:
        print(f"Error inserting data: {e}")


def etl_create_dim_exp_types(connection_params, table_name, destination_table):
    """
    Purpose: Creates a dimension table for expense types.

    :param connection_params: Establishes a connection to the PostgreSQL database
    :param table_name: Retrieves distinct EXP_TYPE and EXP_ID values from the "transactions_silver" table.
    :param destination_table: Writes the retrieved data to a new table named "dim_exp_types" in PostgreSQL.
    :return: dim_exp_types table
    """
    try:
        # Connect to PostgreSQL and read data into a DataFrame
        connection = psycopg2.connect(**connection_params)
        engine = create_engine(
            f'postgresql://{connection_params["user"]}:{connection_params["password"]}@{connection_params["host"]}:{connection_params["port"]}/{connection_params["database"]}')

        # Retrieve unique EXP_TYPE values from the transactions table
        query = f'SELECT DISTINCT exp_type,exp_id FROM {table_name}'
        df = pd.read_sql(query, con=engine)

        df.to_sql(destination_table, con=engine, if_exists='replace', index=False)
        print('exp_types_created')
        # Close the PostgreSQL connection
        connection.close()

    except Exception as e:
        print(f"Error inserting data: {e}")


if __name__ == "__main__":
    create_table()
    time.sleep(15)
    insert_data_in_chunks(csv_file_path, connection_params)
    time.sleep(15)
    create_silver(connection_params=connection_params,table_name='transactions_bronze',destination_table = 'transactions_silver')
    time.sleep(15)
    create_gold(connection_params=connection_params,table_name='transactions_silver',destination_table='transactions_gold')
    time.sleep(15)
    etl_create_dim_customer(connection_params=connection_params,transactions_table = 'transactions_silver', dim_customer_table = 'dim_customer_info')
    time.sleep(15)
    etl_create_dim_exp_types(connection_params=connection_params,table_name='transactions_silver',destination_table='dim_exp_types')
    print('etl completed')
