# spammer/Dockerfile

FROM python:3.10-slim

WORKDIR /app

COPY spammer.py .

RUN pip install requests psycopg2-binary

CMD ["python", "spammer.py"]
