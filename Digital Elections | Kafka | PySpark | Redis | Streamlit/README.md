# 🗳️ Project Overview - Digital Elections (Enhancing Georgian Democracy)

A modern, real-time **Digital Election System** built using **FastAPI**, **Apache Kafka**, **Redis**, **PySpark**, and **Streamlit**.

This project simulates a complete voting pipeline and provides a **live dashboard** for real-time election results.

---

### 🔐 How It Works

- Each voter is assigned a **unique identifier (GUID)**, which must be submitted via the API to verify their identity.
- The identifier is stored in **Redis** as a Key:Value pair for ultra-fast read/write operations.

---

### 🔄 Data Flow

1. **FastAPI** receives the vote (along with GUID and Personal ID) and sends it to **Apache Kafka**.
2. **PySpark** listens to the Kafka stream, processes incoming votes, and **aggregates vote counts by candidate**.
3. Aggregated results are written to **Redis** for low-latency access.
4. **Streamlit** reads live data from Redis and displays real-time visualizations:
   - 📊 **Bar Chart**
   - 🏆 **Candidate Ranking**
   - 🍩 **Donut Chart**

⏱️ The system is optimized for minimal latency (1–5 milliseconds) in data refresh and UI updates.

## 🔧 Tech Stack

- **API Gateway**: FastAPI  
- **Message Broker**: Apache Kafka  
- **Stream Processor**: PySpark  
- **Dashboard**: Streamlit  
- **Key Store**: Redis  
- **Data Storage**: PostgreSQL (optional / extendable)  
- **Containerization**: Docker + Docker Compose  


<img width="407" height="528" alt="image" src="https://github.com/user-attachments/assets/336b2df8-2339-4f82-b89b-1d4098b6a8e4" />


# Project Architecture
<img width="1425" height="791" alt="image" src="https://github.com/user-attachments/assets/25c82055-e6b9-45ea-b6c0-1c9c3cb05f82" />


# Features:
Voter Input: FastAPI endpoint receives votes with secure token (GUID).
Kafka: Streams votes into a votes topic.
PySpark: Aggregates live votes and outputs to aggregated_votes.
Streamlit: Visual dashboard auto-refreshes with real-time results.
Redis: Handles voter key status (used / unused).

🤖 Spammer: Simulates multiple voters for load testing and demo.

# ⚙️ How to Run (with Docker)
1. Clone the Repository - git clone https://github.com/GigiOniani/digital-elections.git
2. Start All Services
docker-compose up --build 

3. Create kafka topic - aggregated_votes

4. Run db_init and redis_init scripts to initialize database and generate voter data.

5. Run spammer.py to simulate elections

6. open streamlit at localhost:8501



# 🗳️ FastAPI Voting Endpoint
POST /vote
{
  "personal_id": "12345678901",
  "guid": "abc-123-def-456",
  "candidate": "John Doe"
}



# 📊 PGSQL Database with Georgian Voter Unique Key and Demographic Information
<img width="1425" height="401" alt="image" src="https://github.com/user-attachments/assets/fb2242e3-672f-4dc6-96ce-dfc1f2b10161" />




# Final Dashboard 

<img width="1804" height="905" alt="image" src="https://github.com/user-attachments/assets/0e8da0c1-5b9b-422d-a1e2-e396b7c05450" />




# 📌 Notes

- **Redis** is initialized with voter `GUID` keys using the `redis_init.py` script. This script reads data from the PostgreSQL database **before voting begins** to preload valid voter identifiers.
- **Stream processing** is implemented using **Structured Streaming** in **PySpark**, enabling real-time vote aggregation.
- Aggregated results can be **persisted to PostgreSQL** or **exported as JSON files** for further analysis or reporting.


# ✅ TODO (Suggestions for Future Improvement)

- Add authentication for vote submission  
- Optimize FastAPI endpoint performance with async functions and routing  
- Implement rate-limiting or spam protection  
- Persist aggregated results to PostgreSQL
- Redis WAL Implementation for persistence
- Deploy the system via Kubernetes and AWS EC2 for production


# 📄 License
MIT License.
Feel free to use and contribute!

