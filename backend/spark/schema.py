from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    BooleanType,
    IntegerType,
)

sensor_schema = StructType([
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

analytics_schema = StructType([
    StructField("_id", StringType(), False),
    StructField("metric", StringType(), False),
    StructField("location_id", StringType(), True),
    StructField("date", StringType(), True),
    StructField("hour", IntegerType(), True),
    StructField("average", DoubleType(), True),
    StructField("minimum", DoubleType(), True),
    StructField("maximum", DoubleType(), True),
    StructField("record_count", IntegerType(), True),
    StructField("processed_at", StringType(), True),
])
