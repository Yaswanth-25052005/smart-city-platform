"""Health and system status endpoints."""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from pymongo.errors import PyMongoError

from backend.api.dependencies import get_mongo_client
from backend.common.logging import get_logger
from backend.config.settings import (
    DATABASE_NAME,
    KAFKA_BOOTSTRAP,
    KAFKA_SENSOR_TOPIC,
    ML_ENABLED,
)

logger = get_logger(__name__)
router = APIRouter(tags=["health"])


def _check_mongodb() -> dict[str, Any]:
    started = time.perf_counter()
    try:
        client = get_mongo_client()
        client.admin.command("ping")
        collections = client[DATABASE_NAME].list_collection_names()
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "status": "up",
            "database": DATABASE_NAME,
            "collections": len(collections),
            "latency_ms": latency_ms,
        }
    except PyMongoError as exc:
        logger.exception("MongoDB health check failed")
        return {"status": "down", "error": str(exc)}


def _check_kafka() -> dict[str, Any]:
    started = time.perf_counter()
    consumer = None
    try:
        consumer = KafkaConsumer(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            consumer_timeout_ms=3000,
            request_timeout_ms=5000,
        )
        topics = sorted(consumer.topics())
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        sensor_topic_present = KAFKA_SENSOR_TOPIC in topics
        return {
            "status": "up",
            "bootstrap_servers": KAFKA_BOOTSTRAP,
            "topics_count": len(topics),
            "sensor_topic_present": sensor_topic_present,
            "latency_ms": latency_ms,
        }
    except NoBrokersAvailable as exc:
        logger.warning("Kafka health check failed: %s", exc)
        return {"status": "down", "error": str(exc)}
    except Exception as exc:
        logger.exception("Kafka health check failed")
        return {"status": "down", "error": str(exc)}
    finally:
        if consumer is not None:
            consumer.close()


@router.get("/health")
def health() -> dict[str, Any]:
    """Platform health endpoint used by Docker and the dashboard."""
    mongodb = _check_mongodb()
    kafka = _check_kafka()

    overall_status = "healthy" if mongodb["status"] == "up" and kafka["status"] == "up" else "degraded"

    payload = {
        "status": overall_status,
        "service": "smart-city-api",
        "mongodb": mongodb,
        "kafka": kafka,
        "ml_enabled": ML_ENABLED,
    }

    logger.info("Health check completed: %s", overall_status)
    return payload
