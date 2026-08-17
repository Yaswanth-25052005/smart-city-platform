from pyspark.sql import DataFrame
import pyspark.sql.functions as F

def clean_data(df: DataFrame) -> DataFrame:
    """
    Clean the raw sensor data by filtering invalid records, dropping duplicates,
    and handling timestamps.
    """
    # 1. Drop records missing critical identification fields
    df = df.dropna(subset=["event_id", "location_id", "timestamp"])

    # 2. Drop duplicates by event_id
    df = df.dropDuplicates(["event_id"])

    # 3. Convert timestamp to Spark TimestampType
    df = df.withColumn("timestamp_col", F.to_timestamp("timestamp"))
    # Filter out rows where timestamp conversion failed
    df = df.filter(F.col("timestamp_col").isNotNull())

    # 4. Enforce reasonable ranges on numeric fields
    # Temperature: -50 to 60 Celsius
    # Humidity: 0 to 100
    # Air Quality: >= 0
    # Noise: >= 0
    df = df.filter(
        (F.col("temperature").isNull() | ((F.col("temperature") >= -50) & (F.col("temperature") <= 60))) &
        (F.col("humidity").isNull() | ((F.col("humidity") >= 0) & (F.col("humidity") <= 100))) &
        (F.col("air_quality").isNull() | (F.col("air_quality") >= 0)) &
        (F.col("noise").isNull() | (F.col("noise") >= 0))
    )

    return df
