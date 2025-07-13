🗳️ Digital Elections
A modern, real-time digital election system built with FastAPI, Apache Kafka, Redis, PySpark, and Streamlit. This project simulates a secure voting pipeline and provides a live dashboard for election results.

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
bash
Copy
Edit
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


<img width="1182" height="660" alt="image" src="https://github.com/user-attachments/assets/4fa02671-b156-4b7a-ba2e-abef17fa5103" />

🚀 Features
🧑‍💻 Voter Input: FastAPI endpoint receives votes with secure token (GUID).

📤 Kafka: Streams votes into a votes topic.

🔥 PySpark: Aggregates live votes and outputs to aggregated_votes.

📊 Streamlit: Visual dashboard auto-refreshes with real-time results.

⚙️ Redis: Handles voter key status (used / unused).

🤖 Spammer: Simulates multiple voters for load testing and demo.

⚙️ How to Run (with Docker)
1. Clone the Repository
bash
Copy
Edit
git clone https://github.com/yourusername/digital-elections.git
cd digital-elections/streamlit_app
2. Start All Services
bash
Copy
Edit
docker-compose up --build
This will spin up:

3. Create kafka topic - aggregated_votes

4. Run 


🗳️ FastAPI Voting Endpoint
POST /vote

json
Copy
Edit
{
  "personal_id": "12345678901",
  "guid": "abc-123-def-456",
  "candidate": "John Doe"
}
✔️ GUID is verified in Redis and marked as used.
✔️ Only valid, unused keys are accepted.

📺 Streamlit Dashboard
Access at:
http://localhost:8501

Displays:

Candidate-wise vote counts

Auto-refresh every few seconds

Real-time Kafka → Spark → Redis pipeline

🧪 Simulate Votes
A dedicated spammer service sends random or targeted votes into the Kafka pipeline for demo/testing.

📌 Notes
Redis is initialized with voter guid keys via redis_init.py.

Stream processing is done using structured streaming in PySpark.

You can persist aggregated results to PostgreSQL or JSON files for further analysis.

✅ TODO (Suggestions for Improvement)
 Add authentication for vote submission
 FastAPI endpoint is really slow, needs async functions and routing for further smooth and secure operations
 Rate-limiting or spam protection
 Persist results to PostgreSQL
 Deploy via Kubernetes and AWS EC2 for production


📄 License
MIT License.
Feel free to use and contribute!

