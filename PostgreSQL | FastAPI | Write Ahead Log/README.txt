The Python project leverages Docker, PostgreSQL (PGSQL), and FastAPI to build a simple API system, ensuring data consistency with a Write-Ahead Log (WAL) that runs every minute to handle failed or pending transactions by updating the production database. The architecture includes a production database and a PGSQL clone for batch processing, supporting user, transaction, and product data tables with defined structures.

short architecture of project:

```
FastAPI_PGSQL/
│
├── venv/                  # Virtual environment root
│
├── app/
│   ├── __init__.py
│   ├── create_db.py       # Database creation script
│   ├── main.py            # FastAPI application entry point
│   ├── replay_wal.py      # WAL replay and processing logic
│   └── spam_transactions.py  # Transaction handling logic
│
├── logs/
│   └── trasnsaction.logs       # Manual Log file for WAL implementation
│
├── docker-compose.yml     # Configures multi-container Docker applications
├── Dockerfile_spammer     # Dockerfile for the spammer service
├── Dockerfile_sync        # Dockerfile for synchronization service
├── .gitignore             # Git ignore file
├── init_db.py             # Initial database setup script
├── requirements.txt       # Python dependencies
└── sync_batch.py          # Synchronization and batch processing script to clone_db
```

This structure organizes the project with the `app` directory containing core scripts like `main.py` for the FastAPI app, `create_db.py` for database setup, `replay_wal.py` for the WAL mechanism, and `spam_transactions.py` for transaction management. The `logs` directory stores runtime logs, while `docker-compose.yml` and related Dockerfiles (`Dockerfile_spammer`, `Dockerfile_sync`) manage containerized services. Additional files like `init_db.py`, `requirements.txt`, and `sync_batch.py` support database initialization, dependencies, and batch processing, respectively.