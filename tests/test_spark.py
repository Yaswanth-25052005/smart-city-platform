import pytest
from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, BooleanType

from backend.spark.cleaning import clean_data
from backend.spark.transformations import apply_transformations
from backend.spark.aggregations import aggregate_metrics
from backend.spark.schema import sensor_schema

@pytest.fixture(scope="module")
def spark():
    return (
        SparkSession.builder
        .master("local[1]")
        .appName("Spark Unit Tests")
        .getOrCreate()
    )

def test_cleaning(spark):
    data = [
        # Valid record
        ("e1", "loc1", "2023-10-27T10:00:00Z", 25.0, 50.0, 10.0, 60.0),
        # Missing event_id
        (None, "loc1", "2023-10-27T10:00:00Z", 25.0, 50.0, 10.0, 60.0),
        # Duplicate event_id
        ("e1", "loc1", "2023-10-27T10:00:00Z", 25.0, 50.0, 10.0, 60.0),
        # Invalid timestamp
        ("e2", "loc1", "invalid_timestamp", 25.0, 50.0, 10.0, 60.0),
        # Invalid temperature (-100)
        ("e3", "loc1", "2023-10-27T10:00:00Z", -100.0, 50.0, 10.0, 60.0),
        # Invalid humidity (150)
        ("e4", "loc1", "2023-10-27T10:00:00Z", 25.0, 150.0, 10.0, 60.0)
    ]
    
    schema = StructType([
        StructField("event_id", StringType(), True),
        StructField("location_id", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("temperature", DoubleType(), True),
        StructField("humidity", DoubleType(), True),
        StructField("air_quality", DoubleType(), True),
        StructField("noise", DoubleType(), True),
    ])
    
    df = spark.createDataFrame(data, schema)
    # add other missing columns from sensor schema
    df = df.withColumn("device_id", df["event_id"])
    df = df.withColumn("parking_occupied", df["event_id"].isNull()) # Dummy
    df = df.withColumn("streetlight_on", df["event_id"].isNull()) # Dummy

    cleaned_df = clean_data(df)
    results = cleaned_df.collect()
    
    # Should only keep "e1" (one copy)
    assert len(results) == 1
    assert results[0].event_id == "e1"

def test_transformations(spark):
    data = [
        ("e1", "loc1", "2023-10-27T10:15:30Z", True, False)
    ]
    schema = StructType([
        StructField("event_id", StringType(), True),
        StructField("location_id", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("parking_occupied", BooleanType(), True),
        StructField("streetlight_on", BooleanType(), True),
    ])
    df = spark.createDataFrame(data, schema)
    
    # Needs timestamp_col created by clean_data
    from pyspark.sql.functions import to_timestamp
    df = df.withColumn("timestamp_col", to_timestamp("timestamp"))
    
    transformed_df = apply_transformations(df)
    results = transformed_df.collect()[0]
    
    assert results.date == "2023-10-27"
    assert results.hour == 10
    assert results.parking_occupied_numeric == 1
    assert results.streetlight_on_numeric == 0

def test_aggregations(spark):
    data = [
        ("loc1", "2023-10-27", 10, 20.0, 40.0, 15.0, 50.0, 1, 0),
        ("loc1", "2023-10-27", 10, 30.0, 60.0, 25.0, 70.0, 1, 1),
        ("loc2", "2023-10-27", 10, 25.0, None, None, None, 0, 1) # loc2 with some nulls
    ]
    schema = StructType([
        StructField("location_id", StringType(), True),
        StructField("date", StringType(), True),
        StructField("hour", StringType(), True), # to test groupby
        StructField("temperature", DoubleType(), True),
        StructField("humidity", DoubleType(), True),
        StructField("air_quality", DoubleType(), True),
        StructField("noise", DoubleType(), True),
        StructField("parking_occupied_numeric", StringType(), True),
        StructField("streetlight_on_numeric", StringType(), True)
    ])
    df = spark.createDataFrame(data, schema)
    
    analytics_df = aggregate_metrics(df)
    
    # We should have metrics for temp, hum, aq, noise, parking, light
    # temp: loc1 avg = 25, loc2 avg = 25
    results = analytics_df.filter(analytics_df.metric == "temperature").collect()
    assert len(results) == 2
    
    loc1_temp = [r for r in results if r.location_id == "loc1"][0]
    assert loc1_temp.average == 25.0
    assert loc1_temp.minimum == 20.0
    assert loc1_temp.maximum == 30.0
    assert loc1_temp.record_count == 2
