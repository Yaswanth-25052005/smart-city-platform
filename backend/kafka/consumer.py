import json

from kafka import KafkaConsumer

from backend.config.settings import (
    KAFKA_BOOTSTRAP,
    TOPIC_NAME
)

from backend.services.validation_service import ValidationService
from backend.database.repository import SensorRepository

consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

print("Consumer Started...\n")

for message in consumer:

    try:

        sensor = ValidationService.validate(message.value)

        SensorRepository.insert(sensor)

        print("Stored:", sensor)

    except Exception as e:

        print(e)