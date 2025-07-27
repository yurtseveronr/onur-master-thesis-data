from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql.functions import from_json, col, year, month, dayofmonth, to_timestamp
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

# Kafka message JSON schema
schema = (
    StructType()
    .add("message", StringType())
    .add("timestamp", StringType())  # ISO 8601 timestamp (e.g., "2025-11-09T12:34:56Z")
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
        ) \
        .withColumn("year", year(col("timestamp"))) \
        .withColumn("month", month(col("timestamp"))) \
        .withColumn("day", dayofmonth(col("timestamp")))

    dyf = DynamicFrame.fromDF(df_parsed, glueContext, "dyf")

    glueContext.writeStream \
        .from_dynamic_frame(dyf) \
        .format("parquet") \
        .option("checkpointLocation", f"s3://onur-master-dataset/kafka/checkpoints/{topic}") \
        .option("path", f"s3://onur-master-dataset/kafka/{topic}") \
        .partitionBy("year", "month", "day") \
        .outputMode("append") \
        .start()
