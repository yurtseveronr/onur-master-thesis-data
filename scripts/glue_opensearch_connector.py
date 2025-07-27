from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql.functions import from_json, col, to_timestamp
from pyspark.sql.types import StructType, StringType
from awsglue.dynamicframe import DynamicFrame

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

topics = [
    'audit_logs', 
    'user_movie_logs', 
    'user_series_logs', 
    'movie_search_logs', 
    'service_search_logs'
]

# Kafka message schema
schema = (
    StructType()
    .add("message", StringType())
    .add("timestamp", StringType())  # ISO 8601 format timestamp
)

for topic in topics:
    df_raw = spark.readStream \
        .format("kafka") \
        .option("connectionName", "kafka-conn") \
        .option("topicName", topic) \
        .option("startingOffsets", "latest") \
        .load()

    df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json_data") \
        .withColumn("json", from_json(col("json_data"), schema)) \
        .select(
            col("json.message").alias("message"),
            to_timestamp(col("json.timestamp")).alias("timestamp")
        )

    dyf = DynamicFrame.fromDF(df_parsed, glueContext, "dyf")

    glueContext.writeStream \
        .from_dynamic_frame(dyf) \
        .format("opensearch") \
        .option("checkpointLocation", f"s3://onur-master-dataset/kafka/checkpoints/{topic}-os") \
        .option("connectionName", "opensearch-conn") \
        .option("indexName", topic) \
        .option("region", "eu-central-1") \
        .option("esBatchSize", "500") \
        .option("esBatchInterval", "5") \
        .outputMode("append") \
        .start()
