# init_db.py
from app import create_transaction_table, create_users_table, create_production_database, conn

def init():
    try:
        print("Creating production database...")
        create_production_database(conn)
        print("Creating users table...")
        create_users_table(conn)
        print("Creating transactions table...")
        create_transaction_table(conn)
        print("✅ All tables created successfully.")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

if __name__ == "__main__":
    init()
