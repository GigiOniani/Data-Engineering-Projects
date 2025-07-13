🗳️ Digital Elections
A modern, real-time digital election system built with FastAPI, Apache Kafka, Redis, PySpark, and Streamlit. This project simulates a voting pipeline and provides a live dashboard for election results.

🔧 Tech Stack
Component	Tech
API Gateway	FastAPI
Message Broker	Apache Kafka
Stream Processor PySpark
Dashboard	Streamlit
Key Store	Redis
Data Storage	PostgreSQL (optional / extendable)
Containerization	Docker + Docker Compose

📁 Project Structure
Digital Elections/
│
├── app/                  # FastAPI microservice
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── spammer/              # Vote simulator (sends spam votes)
│   ├── spammer.py
│   └── Dockerfile
│
├── spark/                # Spark Structured Streaming app
│   ├── spark_app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── streamlit_app/        # Live dashboard
│   ├── streamlit_main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── redis_init.py
│   ├── db_initializer.py
│   └── docker-compose.yaml
│
├── Elections/data/       # Static or uploaded election data
│
├── data/output/          # Spark state/checkpoint storage
│
└── .venv/                # Python virtual environment (optional)




Project Solution Architecture
<img width="6444" height="4604" alt="image" src="https://github.com/user-attachments/assets/50a43bf6-8186-4132-b519-53266357bc9f" />

Features:
Voter Input: FastAPI endpoint receives votes with secure token (GUID).
Kafka: Streams votes into a votes topic.
PySpark: Aggregates live votes and outputs to aggregated_votes.
Streamlit: Visual dashboard auto-refreshes with real-time results.
Redis: Handles voter key status (used / unused).

🤖 Spammer: Simulates multiple voters for load testing and demo.

⚙️ How to Run (with Docker)
1. Clone the Repository - git clone https://github.com/GigiOniani/digital-elections.git
2. Start All Services
docker-compose up --build 

3. Create kafka topic - aggregated_votes

4. Run db_init and redis_init scripts to initialize database and generate voter data.

5. Run spammer.py to simulate elections

6. open streamlit at localhost:8501



🗳️ FastAPI Voting Endpoint
POST /vote
{
  "personal_id": "12345678901",
  "guid": "abc-123-def-456",
  "candidate": "John Doe"
}
✔️ GUID is verified in Redis and marked as used.
✔️ Only valid, unused keys are accepted.


Displays:
Candidate-wise vote counts
Auto-refresh every few seconds
Real-time Kafka → Spark → Redis pipeline

🧪 Simulate Votes - spammer.py
A dedicated spammer service sends random or targeted votes into the Kafka pipeline for demo/testing.

📌 Notes
Redis is initialized with voter guid keys via redis_init.py.
Stream processing is done using structured streaming in PySpark.
You can persist aggregated results to PostgreSQL or JSON files for further analysis.

✅ TODO (Suggestions for Future Improvement)
 Add authentication for vote submission
 FastAPI endpoint is slow, needs async functions and routing for further smooth and secure operations
 Rate-limiting or spam protection
 Persist results to PostgreSQL
 Deploy via Kubernetes and AWS EC2 for production


📄 License
MIT License.
Feel free to use and contribute!

