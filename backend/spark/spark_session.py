from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("Smart City Analytics")
    .master("local[*]")

    .config(
        "spark.mongodb.read.connection.uri",
        "mongodb://admin:password@localhost:27017/smart_city.sensor_data"
    )

    .config(
        "spark.mongodb.write.connection.uri",
        "mongodb://admin:password@localhost:27017/smart_city.analytics"
    )

    .getOrCreate()
)