import os
import sys

# Configure PySpark to use the current virtual environment Python
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pymongo import MongoClient
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    BooleanType,
)

# -------------------------
# Create Spark Session
# -------------------------

spark = (
    SparkSession.builder
    .appName("Smart City Analytics")
    .master("local[1]")  # Use one local worker for Windows
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .config("spark.python.worker.reuse", "false")
    .getOrCreate()
)

print("✅ Spark Started")
print("Spark Version:", spark.version)

# -------------------------
# Connect to MongoDB
# -------------------------

client = MongoClient("mongodb://admin:password@localhost:27017/")

db = client["smart_city"]

collection = db["sensor_data"]

documents = list(collection.find())

print(f"Documents Found: {len(documents)}")

if len(documents) == 0:
    print("No data found in MongoDB.")
    spark.stop()
    exit()

# -------------------------
# Remove MongoDB _id
# -------------------------

for doc in documents:

    doc.pop("_id", None)

    doc["temperature"] = float(doc["temperature"])
    doc["humidity"] = float(doc["humidity"])
    doc["air_quality"] = float(doc["air_quality"])
    doc["noise"] = float(doc["noise"])

# -------------------------
# Define Schema
# -------------------------

schema = StructType([
    StructField("event_id", StringType(), True),
    StructField("device_id", StringType(), True),
    StructField("location_id", StringType(), True),
    StructField("temperature", DoubleType(), True),
    StructField("humidity", DoubleType(), True),
    StructField("air_quality", DoubleType(), True),
    StructField("noise", DoubleType(), True),
    StructField("parking_occupied", BooleanType(), True),
    StructField("streetlight_on", BooleanType(), True),
    StructField("timestamp", StringType(), True),
])

# -------------------------
# Create DataFrame
# -------------------------

df = spark.createDataFrame(documents, schema)

print("\nDataFrame Created Successfully\n")

print("Schema:\n")

df.printSchema()

print("\nNumber of Records:")

print(df.count())

print("\nFirst Five Records:")

print(df.take(5))

spark.stop()