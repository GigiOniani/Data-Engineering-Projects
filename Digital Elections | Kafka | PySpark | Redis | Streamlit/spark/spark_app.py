# from pyspark.sql import SparkSession
# from pyspark.sql.functions import col
#
# # Kafka settings
# kafka_input_topic = "votes"
# kafka_output_topic = "aggregated_votes"
# kafka_bootstrap = "kafka:9092"  # Docker Compose service name
#
# # Create Spark session
# spark = SparkSession.builder \
#     .appName("KafkaVoteAggregator") \
#     .getOrCreate()
#
# # Read Kafka votes
# df = spark.readStream \
#     .format("kafka") \
#     .option("kafka.bootstrap.servers", kafka_bootstrap) \
#     .option("subscribe", kafka_input_topic) \
#     .option("startingOffsets", "earliest") \
#     .option("failOnDataLoss", "false") \
#     .load()
#
# # Extract key-value fields
# votes = df.selectExpr(
#     "CAST(key AS STRING) as guid",
#     "CAST(value AS STRING) as candidate"
# )
#
# # Group and count votes per candidate
# aggregated = votes.groupBy("candidate") \
#     .count() \
#     .withColumnRenamed("count", "unique_voters")
#
# # Convert to Kafka-compatible key-value
# to_kafka = aggregated.selectExpr(
#     "CAST(candidate AS STRING) AS key",
#     "CAST(unique_voters AS STRING) AS value"
# )
#
# # Write aggregated results back to Kafka
# query = to_kafka.writeStream \
#     .format("kafka") \
#     .outputMode("complete") \
#     .option("kafka.bootstrap.servers", kafka_bootstrap) \
#     .option("topic", kafka_output_topic) \
#     .option("checkpointLocation", "/data/checkpoint_v2") \
#     .start()
#
# query.awaitTermination()


from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import redis

kafka_bootstrap = "kafka:9092"
kafka_input_topic = "votes"
checkpoint_dir = "/data/checkpoint_v2"

# Initialize Spark session
spark = SparkSession.builder \
    .appName("KafkaVoteAggregatorWithRedis") \
    .getOrCreate()

# Read from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap) \
    .option("subscribe", kafka_input_topic) \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()

# Extract GUID and candidate name
votes = df.selectExpr(
    "CAST(key AS STRING) as guid",
    "CAST(value AS STRING) as candidate"
)

# Aggregate votes
aggregated = votes.groupBy("candidate").count() \
    .withColumnRenamed("count", "unique_voters")


def write_to_redis(batch_df, batch_id):
    redis_conn = redis.Redis(host="redis", port=6379, decode_responses=True)
    results = batch_df.collect()
    for row in results:
        redis_conn.hset("results", row["candidate"], row["unique_voters"])
    print(f"Batch {batch_id} written to Redis")

# Start streaming with foreachBatch
query = aggregated.writeStream \
    .foreachBatch(write_to_redis) \
    .outputMode("complete") \
    .option("checkpointLocation", checkpoint_dir) \
    .start()

query.awaitTermination()
