import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .master("local[1]")
    .appName("Simple Test")
    .getOrCreate()
)

data = [
    ("A", 10),
    ("B", 20),
    ("C", 30),
]

df = spark.createDataFrame(data, ["name", "value"])

print(df.count())

df.show()

spark.stop()