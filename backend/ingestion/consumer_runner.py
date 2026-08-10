"""Docker entry point for Kafka ingestion (preserves legacy consumer module)."""

from __future__ import annotations

import json
import signal
import sys

from kafka import KafkaConsumer

from backend.common.logging import get_logger, setup_logging
from backend.config.settings import KAFKA_BOOTSTRAP, TOPIC_NAME
from backend.database.repository import SensorRepository
from backend.services.validation_service import ValidationService

logger = get_logger(__name__)
_running = True


def _handle_shutdown(signum, _frame) -> None:
    global _running
    logger.info("Shutdown signal received (%s)", signum)
    _running = False


def run_consumer() -> None:
    """Consume sensor events from Kafka and persist validated records to MongoDB."""
    setup_logging()
    signal.signal(signal.SIGINT, _handle_shutdown)
    signal.signal(signal.SIGTERM, _handle_shutdown)

    logger.info(
        "Starting ingestion consumer | bootstrap=%s topic=%s",
        KAFKA_BOOTSTRAP,
        TOPIC_NAME,
    )

    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_deserializer=lambda payload: json.loads(payload.decode("utf-8")),
        group_id="smart-city-ingestion",
        auto_offset_reset="latest",
        enable_auto_commit=True,
    )

    try:
        while _running:
            polled = consumer.poll(timeout_ms=1000, max_records=100)
            if not polled:
                continue

            for _, messages in polled.items():
                for message in messages:
                    try:
                        sensor = ValidationService.validate(message.value)
                        SensorRepository.insert(sensor)
                        logger.info("Stored sensor event from device=%s", sensor.get("device_id"))
                    except Exception:
                        logger.exception("Failed to process Kafka message")
    finally:
        consumer.close()
        logger.info("Ingestion consumer stopped")


if __name__ == "__main__":
    try:
        run_consumer()
    except Exception:
        logger.exception("Ingestion consumer crashed")
        sys.exit(1)
