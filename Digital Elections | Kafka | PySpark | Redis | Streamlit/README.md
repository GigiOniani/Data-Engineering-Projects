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

<img width="407" height="528" alt="image" src="https://github.com/user-attachments/assets/336b2df8-2339-4f82-b89b-1d4098b6a8e4" />


Project Solution Architecture
<img width="1425" height="791" alt="image" src="https://github.com/user-attachments/assets/25c82055-e6b9-45ea-b6c0-1c9c3cb05f82" />


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

