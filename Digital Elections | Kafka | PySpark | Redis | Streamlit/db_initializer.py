import uuid
import random
import psycopg2
from faker import Faker

fake = Faker("ka_GE")

parties = [
    "Georgian Dream", "United National Movement", "Lelo for Georgia",
    "European Georgia", "Alliance of Patriots of Georgia", "Girchi",
    "Strategy Aghmashenebeli", "Labor Party of Georgia",
    "Republican Party", "Citizens"
]

leaders = [
    "Irakli Kobakhidze", "Levan Khabeishvili", "Mamuka Khazaradze",
    "Giga Bokeria", "Irma Inashvili", "Zurab Girchi Jafaridze",
    "Giorgi Vashadze", "Shalva Natelashvili",
    "Khatuna Samnidze", "Aleko Elisashvili"
]


def connect():
    return psycopg2.connect(
        dbname='elections',
        user='postgres',
        password='postgres',
        host='postgres',
        port=5432
    )


def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_leaders (
            ID SERIAL PRIMARY KEY,
            leader_name VARCHAR(280),
            political_party VARCHAR(280)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_voters (
            personal_id BIGINT PRIMARY KEY,
            name VARCHAR(280),
            age INT,
            address VARCHAR(280),
            phone_number VARCHAR(280),
            job VARCHAR(280),
            token VARCHAR(280),
            status VARCHAR(280)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trs_voting (
            ID SERIAL PRIMARY KEY,
            leader_name VARCHAR(280),
            timestamp TIMESTAMP,
            transaction_id VARCHAR(280)
        );
    """)
    conn.commit()
    cursor.close()


def insert_leaders(conn):
    cursor = conn.cursor()
    for leader, party in zip(leaders, parties):
        cursor.execute("SELECT COUNT(*) FROM dim_leaders WHERE leader_name = %s", (leader,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO dim_leaders (leader_name, political_party)
                VALUES (%s, %s)
            """, (leader, party))
            print(f"Inserted leader {leader}")
    conn.commit()
    cursor.close()


def insert_voters(conn, count=3540523):
    cursor = conn.cursor()
    for _ in range(count):
        voter = {
            "personal_id": random.randint(10000000000, 99999999999),
            "name": fake.name(),
            "age": random.randint(18, 90),
            "address": fake.address(),
            "phone_number": fake.phone_number(),
            "job": fake.job(),
            "token": str(uuid.uuid4()),
            "status": "Unused"
        }
        try:
            cursor.execute("""
                INSERT INTO dim_voters (personal_id, name, age, address, phone_number, job, token, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                voter["personal_id"], voter["name"], voter["age"],
                voter["address"], voter["phone_number"], voter["job"], voter["token"], voter["status"]
            ))
        except Exception as e:
            conn.rollback()
            print("Duplicate or error:", e)
        else:
            conn.commit()
    cursor.close()


if __name__ == '__main__':
    conn = connect()
    create_tables(conn)
    insert_leaders(conn)
    insert_voters(conn,100000 )
    conn.close()
