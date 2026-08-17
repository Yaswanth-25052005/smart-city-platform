from pyspark.sql import DataFrame
import pyspark.sql.functions as F
from functools import reduce

def aggregate_metrics(df: DataFrame) -> DataFrame:
    """
    Generate aggregations for all metrics and combine them into a single 
    analytics DataFrame matching the analytics_schema.
    """
    processed_at = F.current_timestamp().cast("string")
    
    # Common group by columns
    group_cols = ["location_id", "date", "hour"]
    
    # Helper to format a metric dataframe to the common schema
    def format_metric_df(metric_df: DataFrame, metric_name: str) -> DataFrame:
        return metric_df.select(
            F.concat_ws("_", F.lit(metric_name), F.col("location_id"), F.col("date"), F.col("hour")).alias("_id"),
            F.lit(metric_name).alias("metric"),
            F.col("location_id"),
            F.col("date"),
            F.col("hour"),
            F.col("average").cast("double"),
            F.col("minimum").cast("double"),
            F.col("maximum").cast("double"),
            F.col("record_count").cast("integer"),
            F.lit(None).alias("processed_at") # We will fill this at the end
        ).withColumn("processed_at", processed_at)

    # 1. Temperature
    temp_df = df.filter(F.col("temperature").isNotNull()).groupBy(*group_cols).agg(
        F.avg("temperature").alias("average"),
        F.min("temperature").alias("minimum"),
        F.max("temperature").alias("maximum"),
        F.count("temperature").alias("record_count")
    )
    temp_res = format_metric_df(temp_df, "temperature")

    # 2. Humidity
    hum_df = df.filter(F.col("humidity").isNotNull()).groupBy(*group_cols).agg(
        F.avg("humidity").alias("average"),
        F.min("humidity").alias("minimum"),
        F.max("humidity").alias("maximum"),
        F.count("humidity").alias("record_count")
    )
    hum_res = format_metric_df(hum_df, "humidity")

    # 3. Air Quality
    aq_df = df.filter(F.col("air_quality").isNotNull()).groupBy(*group_cols).agg(
        F.avg("air_quality").alias("average"),
        F.min("air_quality").alias("minimum"),
        F.max("air_quality").alias("maximum"),
        F.count("air_quality").alias("record_count")
    )
    aq_res = format_metric_df(aq_df, "air_quality")

    # 4. Noise
    noise_df = df.filter(F.col("noise").isNotNull()).groupBy(*group_cols).agg(
        F.avg("noise").alias("average"),
        F.min("noise").alias("minimum"),
        F.max("noise").alias("maximum"),
        F.count("noise").alias("record_count")
    )
    noise_res = format_metric_df(noise_df, "noise")

    # 5. Smart Parking
    park_df = df.filter(F.col("parking_occupied_numeric").isNotNull()).groupBy(*group_cols).agg(
        F.avg("parking_occupied_numeric").alias("average"), # Percentage occupancy
        F.min("parking_occupied_numeric").alias("minimum"),
        F.max("parking_occupied_numeric").alias("maximum"),
        F.count("parking_occupied_numeric").alias("record_count")
    )
    park_res = format_metric_df(park_df, "parking")

    # 6. Street Lighting
    light_df = df.filter(F.col("streetlight_on_numeric").isNotNull()).groupBy(*group_cols).agg(
        F.avg("streetlight_on_numeric").alias("average"), # Percentage active
        F.min("streetlight_on_numeric").alias("minimum"),
        F.max("streetlight_on_numeric").alias("maximum"),
        F.count("streetlight_on_numeric").alias("record_count")
    )
    light_res = format_metric_df(light_df, "streetlight")

    # Union all dataframes
    all_metrics = [temp_res, hum_res, aq_res, noise_res, park_res, light_res]
    analytics_df = reduce(DataFrame.unionByName, all_metrics)

    return analytics_df
