"""Spark daemon for Docker — keeps a local Spark session alive (no Hadoop/HDFS)."""

from __future__ import annotations

import signal
import sys
import time

from backend.common.logging import get_logger, setup_logging
from backend.config.settings import SPARK_APP_NAME, SPARK_MASTER

logger = get_logger(__name__)
_running = True


def _handle_shutdown(signum, _frame) -> None:
    global _running
    logger.info("Shutdown signal received (%s)", signum)
    _running = False


def run_spark_daemon() -> None:
    setup_logging()
    signal.signal(signal.SIGINT, _handle_shutdown)
    signal.signal(signal.SIGTERM, _handle_shutdown)

    from pyspark.sql import SparkSession

    logger.info("Starting Spark daemon | master=%s app=%s", SPARK_MASTER, SPARK_APP_NAME)

    spark = (
        SparkSession.builder.appName(SPARK_APP_NAME)
        .master(SPARK_MASTER)
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )

    logger.info("Spark session ready | version=%s", spark.version)

    try:
        while _running:
            count = spark.range(1).count()
            logger.info("Spark heartbeat OK | smoke_test_count=%s", count)
            time.sleep(60)
    finally:
        spark.stop()
        logger.info("Spark daemon stopped")


if __name__ == "__main__":
    try:
        run_spark_daemon()
    except Exception:
        logger.exception("Spark daemon crashed")
        sys.exit(1)
