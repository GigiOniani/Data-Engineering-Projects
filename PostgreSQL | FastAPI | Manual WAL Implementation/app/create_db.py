import os
import psycopg2
# Load DB connection settings from environment variables
DB_HOST = os.getenv("DB_HOST", "db")  # should be 'db' inside Docker
DB_PORT = os.getenv("DB_PORT", "5432")       # port inside container
DB_NAME = os.getenv("DB_NAME", "app_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

import psycopg2

conn = psycopg2.connect(
    host="db",
    port=5432,
    dbname="app_db",
    user="postgres",              # or the correct username
    password="postgres"      # this must be correct
)


def create_production_database(connection):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute("CREATE DATABASE db_production;")
        print("Production database created successfully!")
    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        cursor.close()

def create_transaction_table(connection):
    cursor = connection.cursor()
    try:
        # Drop the existing table if it exists
        cursor.execute("DROP TABLE IF EXISTS transactions;")

        # Create the table with appropriate schema
        cursor.execute("""
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
        connection.commit()
        print("Transactions table created successfully.")
    except Exception as e:
        print(f"Error creating transactions table: {e}")
        connection.rollback()
    finally:
        cursor.close()



def create_users_table(connection):
    cursor = connection.cursor()
    try:
        cursor.execute("DROP TABLE IF EXISTS users;")
        cursor.execute("""
            CREATE TABLE users (
                user_id VARCHAR(255),
                name VARCHAR(255),
                phonenumber VARCHAR(255),
                birthdate DATE,
                worklocation VARCHAR(255),
                gender VARCHAR(255),
                city VARCHAR(255)
            );
        """)
        connection.commit()
        print("Table 'users' created successfully.")
    except Exception as e:
        print(f"Error creating users table: {e}")
    finally:
        cursor.close()



