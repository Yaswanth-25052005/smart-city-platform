import os
from pyspark.sql import SparkSession

def get_spark_session(app_name="Smart City Analytics"):
    # Read MongoDB configs with fallbacks to defaults in case env is not set locally
    mongo_user = os.environ.get("MONGO_USER", "admin")
    mongo_password = os.environ.get("MONGO_PASSWORD", "password")
    mongo_database = os.environ.get("MONGO_DATABASE", "smart_city")
    mongo_uri = os.environ.get(
        "MONGO_URI",
        f"mongodb://{mongo_user}:{mongo_password}@localhost:27017/"
    )
    
    spark_master = os.environ.get("SPARK_MASTER", "local[*]")
    
    # We use packages to download the mongo-spark-connector dynamically.
    spark = (
        SparkSession.builder
        .appName(app_name)
        .master(spark_master)
        .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.3.0")
        .config("spark.mongodb.read.connection.uri", f"{mongo_uri}")
        .config("spark.mongodb.read.database", mongo_database)
        .config("spark.mongodb.read.collection", "sensor_data")
        .config("spark.mongodb.write.connection.uri", f"{mongo_uri}")
        .config("spark.mongodb.write.database", mongo_database)
        .config("spark.mongodb.write.collection", "analytics")
        .getOrCreate()
    )
    
    # Set log level to avoid overwhelming stdout
    spark.sparkContext.setLogLevel("WARN")
    
    return spark