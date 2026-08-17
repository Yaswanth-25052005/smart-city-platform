from pyspark.sql import DataFrame

def write_analytics(df: DataFrame) -> None:
    """
    Write the analytics DataFrame to MongoDB.
    Relies on SparkSession configs for connection URI and collection name.
    """
    (
        df.write
        .format("mongodb")
        .mode("append")
        .option("operationType", "replace") # Use replace to enable upserts based on _id
        .save()
    )
