"""One-shot Spark health check used by Docker healthcheck."""

from __future__ import annotations

import sys

from pyspark.sql import SparkSession

from backend.config.settings import SPARK_APP_NAME, SPARK_MASTER


def main() -> int:
    spark = (
        SparkSession.builder.appName(f"{SPARK_APP_NAME}-health")
        .master(SPARK_MASTER)
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    try:
        assert spark.range(1).count() == 1
        print("spark_ok")
        return 0
    finally:
        spark.stop()


if __name__ == "__main__":
    sys.exit(main())
