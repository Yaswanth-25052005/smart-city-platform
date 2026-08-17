from pyspark.sql import DataFrame
import pyspark.sql.functions as F
from pyspark.sql.types import IntegerType

def apply_transformations(df: DataFrame) -> DataFrame:
    """
    Apply feature engineering and transformations.
    Add date, hour, day_of_week and categorical/numeric derivations.
    """
    # Date and Hour extraction
    df = df.withColumn("date", F.date_format(F.col("timestamp_col"), "yyyy-MM-dd"))
    df = df.withColumn("hour", F.hour(F.col("timestamp_col")))
    df = df.withColumn("day_of_week", F.dayofweek(F.col("timestamp_col")))

    # Numeric conversions for booleans
    df = df.withColumn(
        "parking_occupied_numeric",
        F.when(F.col("parking_occupied") == True, 1)
         .when(F.col("parking_occupied") == False, 0)
         .otherwise(None).cast(IntegerType())
    )

    df = df.withColumn(
        "streetlight_on_numeric",
        F.when(F.col("streetlight_on") == True, 1)
         .when(F.col("streetlight_on") == False, 0)
         .otherwise(None).cast(IntegerType())
    )

    return df
