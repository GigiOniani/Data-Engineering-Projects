FROM bitnami/spark:3.5.0

USER root

RUN apt-get update && apt-get install -y \
    python3 python3-pip wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

COPY spark_app.py /opt/spark-app.py

RUN mkdir -p /data/output /data/checkpoint && chown -R 1001:1001 /data

# Download necessary jars including commons-pool2
RUN wget https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.0/spark-sql-kafka-0-10_2.12-3.5.0.jar -P /opt/bitnami/spark/jars/ && \
    wget https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.0/spark-token-provider-kafka-0-10_2.12-3.5.0.jar -P /opt/bitnami/spark/jars/ && \
    wget https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.1/kafka-clients-3.5.1.jar -P /opt/bitnami/spark/jars/ && \
    wget https://repo1.maven.org/maven2/org/scala-lang/scala-library/2.12.18/scala-library-2.12.18.jar -P /opt/bitnami/spark/jars/ && \
    wget https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar -P /opt/bitnami/spark/jars/

USER 1001

CMD ["/opt/bitnami/spark/bin/spark-submit", "/opt/spark-app.py"]
