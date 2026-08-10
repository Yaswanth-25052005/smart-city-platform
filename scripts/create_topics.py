"""Create Kafka topics required by the platform."""

from __future__ import annotations

import sys

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from backend.common.logging import get_logger, setup_logging
from backend.config.settings import (
    KAFKA_ALERT_TOPIC,
    KAFKA_ANALYTICS_TOPIC,
    KAFKA_BOOTSTRAP,
    KAFKA_SENSOR_TOPIC,
)

logger = get_logger(__name__)

TOPICS = [
    KAFKA_SENSOR_TOPIC,
    KAFKA_ALERT_TOPIC,
    KAFKA_ANALYTICS_TOPIC,
]


def create_topics() -> None:
    setup_logging()
    admin = KafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP, client_id="smart-city-init")
    new_topics = [NewTopic(name=topic, num_partitions=1, replication_factor=1) for topic in TOPICS]

    try:
        admin.create_topics(new_topics=new_topics, validate_only=False)
        logger.info("Created Kafka topics: %s", ", ".join(TOPICS))
    except TopicAlreadyExistsError:
        logger.info("Kafka topics already exist: %s", ", ".join(TOPICS))
    except Exception:
        logger.exception("Failed to create Kafka topics")
        raise
    finally:
        admin.close()


if __name__ == "__main__":
    try:
        create_topics()
    except Exception:
        sys.exit(1)
