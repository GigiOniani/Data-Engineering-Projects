FROM python:3.10-slim

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure streamlit-autorefresh is installed (if not in requirements.txt)
RUN pip install --no-cache-dir streamlit-autorefresh

# Copy application code into the container
COPY . .

# Expose Streamlit default port (optional for clarity)
EXPOSE 8501

# Launch Streamlit app
CMD ["streamlit", "run", "streamlit_main.py", "--server.port=8501", "--server.address=0.0.0.0"]
