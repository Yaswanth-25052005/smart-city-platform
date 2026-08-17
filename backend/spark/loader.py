from pyspark.sql import DataFrame, SparkSession
from backend.spark.schema import sensor_schema

def load_sensor_data(spark: SparkSession) -> DataFrame:
    """
    Load raw sensor data from MongoDB into a Spark DataFrame.
    """
    df = (
        spark.read
        .format("mongodb")
        .schema(sensor_schema)
        .load()
    )
    return df
